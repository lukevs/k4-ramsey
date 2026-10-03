// Exact unit-weight, blue-diagonal K4 search. Lean independently recounts results.
#include "search.h"

#include <algorithm>
#include <array>
#include <cstdio>
#include <exception>
#include <limits>
#include <new>
#include <stdexcept>
#include <vector>

namespace {
using Word = uint64_t;
using Count = int64_t;
constexpr int word_bits = 64;
constexpr int max_words = (K4_MAX_ORDER + word_bits - 1) / word_bits;
using VertexSet = std::array<Word, max_words>;
constexpr Count edge_coefficient = 14;
constexpr Count triangle_coefficient = 36;
constexpr Count clique_coefficient = 24;
// The full numerator is at most n^4. All subgraph counts and mixed differences
// also fit in signed 64 bits for this deliberately bounded backend.
static_assert(Count(K4_MAX_ORDER) * K4_MAX_ORDER * K4_MAX_ORDER * K4_MAX_ORDER
              < std::numeric_limits<Count>::max());

class Graph {
public:
    explicit Graph(int order, const uint8_t* matrix);
    int order() const noexcept { return order_; }
    bool has_edge(int u, int v) const noexcept;
    void flip_edge(int u, int v) noexcept;
    Count calculate_delta(int u, int v) const noexcept;
    K4Counts count_subgraphs() const noexcept;
    void export_matrix(uint8_t* out) const noexcept;
    void enable_cache();
    bool has_cache() const noexcept { return !cached_.empty(); }
    Count read_cached_delta(int u, int v) const noexcept { return cached_[u * order_ + v]; }
    K4Flip find_best_flip(const int* expiry = nullptr, int step = 0, Count aspiration = 0) const noexcept;
    K4Star find_best_star(int per_color) const;

private:
    // Invariants: symmetric, disjoint red/blue rows; their union is every
    // off-diagonal valid bit. Padding and diagonals are zero. A present cache
    // holds the exact current delta for every unordered edge (stored twice).
    int order_, words_;
    std::vector<Word> red_, blue_;
    std::vector<Count> cached_;

    Count count_induced_edges(const std::vector<Word>& rows, const VertexSet& vertices) const noexcept;
    Count count_four_cliques(const std::vector<Word>& rows) const noexcept;
    void add_cached_delta(int u, int v, Count change) noexcept;
    void update_cache_before_flip(int u, int v) noexcept;
};

thread_local int last_error_code = K4_OK;
thread_local char last_error_message[256] = {};

void record_error(int code, const char* message) noexcept {
    last_error_code = code;
    std::snprintf(last_error_message, sizeof(last_error_message), "%s", message);
}

// The sole exception boundary. Error recording itself cannot allocate or throw.
template<class Action>
int run_checked(Action action) noexcept {
    record_error(K4_OK, "");
    try {
        action();
        return 1;
    } catch (const std::bad_alloc&) {
        record_error(K4_OUT_OF_MEMORY, "native allocation failed");
    } catch (const std::invalid_argument& error) {
        record_error(K4_INVALID_ARGUMENT, error.what());
    } catch (const std::exception& error) {
        record_error(K4_INTERNAL_ERROR, error.what());
    } catch (...) {
        record_error(K4_INTERNAL_ERROR, "unknown native exception");
    }
    return 0;
}

void require(bool condition, const char* message) {
    if (!condition) throw std::invalid_argument(message);
}

Graph& require_graph(void* handle) {
    require(handle != nullptr, "null graph handle");
    return *static_cast<Graph*>(handle);
}

void require_edge(const Graph& graph, int u, int v) {
    require(u >= 0 && u < graph.order() && v >= 0 && v < graph.order() && u != v,
            "invalid edge endpoints");
}

void require_cache(const Graph& graph) {
    require(graph.has_cache(), "delta cache has not been enabled");
}

void validate_batch(const Graph& graph, const int* us, const int* vs, int size, const Count* out) {
    require(size >= 0, "negative batch size");
    require(size == 0 || (us && vs && out), "null batch buffer");
    // Check the entire batch before writing any output.
    for (int i = 0; i < size; ++i) require_edge(graph, us[i], vs[i]);
}
} // namespace

// Public ABI first: all operations are checked and no C++ exception escapes.
extern "C" {
int k4_error_code() noexcept { return last_error_code; }
const char* k4_last_error() noexcept { return last_error_message; }

void* k4_new(int n, const uint8_t* matrix) noexcept {
    Graph* result = nullptr;
    run_checked([&] {
        require(n >= 1 && n <= K4_MAX_ORDER, "order must be 1..1024");
        require(matrix != nullptr, "null adjacency matrix");
        for (int i = 0; i < n; ++i) {
            require(matrix[i * n + i] == 0, "diagonal must be blue");
            for (int j = 0; j < n; ++j) {
                require(matrix[i * n + j] <= 1, "matrix must be binary");
                require(matrix[i * n + j] == matrix[j * n + i], "matrix must be symmetric");
            }
        }
        result = new Graph(n, matrix);
    });
    return result;
}

void k4_free(void* handle) noexcept {
    run_checked([&] { delete static_cast<Graph*>(handle); });
}

void k4_flip(void* handle, int u, int v) noexcept {
    run_checked([&] {
        auto& graph = require_graph(handle);
        require_edge(graph, u, v);
        graph.flip_edge(u, v);
    });
}

Count k4_delta(void* handle, int u, int v) noexcept {
    Count result = 0;
    run_checked([&] {
        auto& graph = require_graph(handle);
        require_edge(graph, u, v);
        result = graph.calculate_delta(u, v);
    });
    return result;
}

void k4_deltas(void* handle, const int* us, const int* vs, int size, Count* out) noexcept {
    run_checked([&] {
        auto& graph = require_graph(handle);
        validate_batch(graph, us, vs, size, out);
        for (int i = 0; i < size; ++i) out[i] = graph.calculate_delta(us[i], vs[i]);
    });
}

void k4_export(void* handle, uint8_t* out) noexcept {
    run_checked([&] {
        auto& graph = require_graph(handle);
        require(out != nullptr, "null matrix output");
        graph.export_matrix(out);
    });
}

int k4_enable_cache(void* handle) noexcept {
    return run_checked([&] { require_graph(handle).enable_cache(); });
}

Count k4_cached_delta(void* handle, int u, int v) noexcept {
    Count result = 0;
    run_checked([&] {
        auto& graph = require_graph(handle);
        require_edge(graph, u, v);
        require_cache(graph);
        result = graph.read_cached_delta(u, v);
    });
    return result;
}

void k4_cached_deltas(void* handle, const int* us, const int* vs, int size, Count* out) noexcept {
    run_checked([&] {
        auto& graph = require_graph(handle);
        require_cache(graph);
        validate_batch(graph, us, vs, size, out);
        for (int i = 0; i < size; ++i) out[i] = graph.read_cached_delta(us[i], vs[i]);
    });
}

int k4_count_subgraphs(void* handle, K4Counts* out) noexcept {
    return run_checked([&] {
        auto& graph = require_graph(handle);
        require(out != nullptr, "null count output");
        *out = graph.count_subgraphs();
    });
}

int k4_find_best_flip(void* handle, K4Flip* out) noexcept {
    return run_checked([&] {
        auto& graph = require_graph(handle);
        require(out != nullptr, "null flip output");
        require_cache(graph);
        *out = graph.find_best_flip();
    });
}

int k4_find_allowed_flip(void* handle, const int* expiry, int step, Count aspiration, K4Flip* out) noexcept {
    return run_checked([&] {
        auto& graph = require_graph(handle);
        require(out != nullptr && expiry != nullptr, "null tabu buffer");
        require(step >= 0, "negative tabu step");
        require_cache(graph);
        *out = graph.find_best_flip(expiry, step, aspiration);
    });
}

int k4_find_best_star(void* handle, int per_color, K4Star* out) noexcept {
    return run_checked([&] {
        auto& graph = require_graph(handle);
        require(out != nullptr, "null star output");
        require(per_color >= 1 && per_color <= K4_MAX_ORDER, "per_color must be 1..1024");
        require_cache(graph);
        *out = graph.find_best_star(per_color);
    });
}

// Historical positional-output APIs delegate to the same implementation.
void k4_counts(void* handle, Count* out) noexcept {
    K4Counts counts{};
    if (k4_count_subgraphs(handle, out ? &counts : nullptr)) {
        out[0] = counts.red_edges; out[1] = counts.blue_triangles;
        out[2] = counts.red_k4; out[3] = counts.blue_k4; out[4] = counts.numerator;
    }
}
void k4_best_cached(void* handle, Count* out) noexcept {
    K4Flip move{};
    if (k4_find_best_flip(handle, out ? &move : nullptr)) {
        out[0] = move.u; out[1] = move.v; out[2] = move.delta;
    }
}
void k4_best_cached_allowed(void* handle, const int* expiry, int step, Count aspiration, Count* out) noexcept {
    K4Flip move{};
    if (k4_find_allowed_flip(handle, expiry, step, aspiration, out ? &move : nullptr)) {
        out[0] = move.u; out[1] = move.v; out[2] = move.delta;
    }
}
void k4_best_cached_star(void* handle, int per_color, Count* out) noexcept {
    K4Star move{};
    if (k4_find_best_star(handle, per_color, out ? &move : nullptr)) {
        out[0] = move.center; out[1] = move.blue_neighbor;
        out[2] = move.red_neighbor; out[3] = move.delta;
    }
}
} // extern "C"

namespace {
Graph::Graph(int order, const uint8_t* matrix)
    : order_(order), words_((order + word_bits - 1) / word_bits),
      red_(order * words_), blue_(order * words_) {
    for (int i = 0; i < order_; ++i) {
        for (int j = 0; j < order_; ++j) {
            if (i != j) (matrix[i * order_ + j] ? red_ : blue_)[i * words_ + j / word_bits]
                |= Word(1) << (j % word_bits);
        }
    }
}

void Graph::flip_edge(int u, int v) noexcept {
    if (has_cache()) update_cache_before_flip(u, v);
    for (auto* rows : {&red_, &blue_}) {
        (*rows)[u * words_ + v / word_bits] ^= Word(1) << (v % word_bits);
        (*rows)[v * words_ + u / word_bits] ^= Word(1) << (u % word_bits);
    }
}

Count Graph::calculate_delta(int u, int v) const noexcept {
    VertexSet red_common{}, blue_common{};
    Count common = 0;
    for (int word = 0; word < words_; ++word) {
        red_common[word] = red_[u * words_ + word] & red_[v * words_ + word];
        blue_common[word] = blue_[u * words_ + word] & blue_[v * words_ + word];
        common += __builtin_popcountll(blue_common[word]);
    }
    const Count add_red = -edge_coefficient - triangle_coefficient * common
        - clique_coefficient * count_induced_edges(blue_, blue_common)
        + clique_coefficient * count_induced_edges(red_, red_common);
    return has_edge(u, v) ? -add_red : add_red;
}

K4Counts Graph::count_subgraphs() const noexcept {
    K4Counts result{};
    for (auto word : red_) result.red_edges += __builtin_popcountll(word);
    result.red_edges /= 2;
    for (int i = 0; i < order_; ++i) {
        for (int j = i + 1; j < order_; ++j) {
            if (!has_edge(i, j)) {
                for (int word = 0; word < words_; ++word)
                    result.blue_triangles += __builtin_popcountll(blue_[i * words_ + word] & blue_[j * words_ + word]);
            }
        }
    }
    result.blue_triangles /= 3;
    result.red_k4 = count_four_cliques(red_);
    result.blue_k4 = count_four_cliques(blue_);
    result.numerator = order_ + edge_coefficient * (Count(order_) * (order_ - 1) / 2 - result.red_edges)
        + triangle_coefficient * result.blue_triangles + clique_coefficient * (result.red_k4 + result.blue_k4);
    return result;
}

void Graph::export_matrix(uint8_t* out) const noexcept {
    for (int i = 0; i < order_; ++i)
        for (int j = 0; j < order_; ++j) out[i * order_ + j] = has_edge(i, j);
}

void Graph::enable_cache() {
    if (has_cache()) return;
    // Build privately and commit only after success. Allocation failure leaves
    // the original graph and cache state untouched.
    std::vector<Count> cache(order_ * order_, 0);
    for (int u = 0; u < order_; ++u)
        for (int v = u + 1; v < order_; ++v)
            cache[u * order_ + v] = cache[v * order_ + u] = calculate_delta(u, v);
    cached_.swap(cache);
}

K4Flip Graph::find_best_flip(const int* expiry, int step, Count aspiration) const noexcept {
    K4Flip best{-1, -1, 0};
    for (int u = 0; u < order_; ++u) {
        for (int v = u + 1; v < order_; ++v) {
            Count delta = read_cached_delta(u, v);
            bool allowed = !expiry || expiry[u * order_ + v] <= step || delta < aspiration;
            if (allowed && (best.u < 0 || delta < best.delta)) best = {u, v, delta};
        }
    }
    return best;
}

K4Star Graph::find_best_star(int per_color) const {
    K4Star best{-1, -1, -1, 0};
    std::vector<std::pair<Count, int>> chosen[2];
    for (int u = 0; u < order_; ++u) {
        chosen[0].clear(); chosen[1].clear();
        for (int v = 0; v < order_; ++v)
            if (u != v) chosen[has_edge(u, v)].push_back({read_cached_delta(u, v), v});
        for (auto& choices : chosen) {
            int size = std::min(per_color, static_cast<int>(choices.size()));
            std::partial_sort(choices.begin(), choices.begin() + size, choices.end());
            choices.resize(size);
        }
        for (const auto& first : chosen[0]) {
            for (const auto& second : chosen[1]) {
                int v = first.second, w = second.second;
                bool color = has_edge(v, w);
                const auto& rows = color ? red_ : blue_;
                Count triples = 0;
                for (int word = 0; word < words_; ++word)
                    triples += __builtin_popcountll(rows[u * words_ + word] & rows[v * words_ + word] & rows[w * words_ + word]);
                Count delta = first.first + second.first - clique_coefficient * triples - (color ? 0 : triangle_coefficient);
                if (delta < best.delta) best = {u, v, w, delta};
            }
        }
    }
    return best;
}

Count Graph::count_four_cliques(const std::vector<Word>& rows) const noexcept {
    Count total = 0;
    for (int i = 0; i < order_; ++i) {
        for (int j = i + 1; j < order_; ++j) {
            if ((rows[i * words_ + j / word_bits] >> (j % word_bits)) & 1) {
                VertexSet common{};
                for (int word = j / word_bits; word < words_; ++word)
                    common[word] = rows[i * words_ + word] & rows[j * words_ + word];
                common[j / word_bits] &= j % word_bits == word_bits - 1 ? 0 : (~Word(0) << (j % word_bits + 1));
                total += count_induced_edges(rows, common);
            }
        }
    }
    return total;
}

Count Graph::count_induced_edges(const std::vector<Word>& rows, const VertexSet& vertices) const noexcept {
    Count twice = 0;
    for (int a = 0; a < words_; ++a) {
        Word bits = vertices[a];
        while (bits) {
            int v = word_bits * a + __builtin_ctzll(bits);
            bits &= bits - 1;
            for (int b = 0; b < words_; ++b) twice += __builtin_popcountll(rows[v * words_ + b] & vertices[b]);
        }
    }
    return twice / 2;
}

void Graph::update_cache_before_flip(int u, int v) noexcept {
    // Mixed finite differences use OLD adjacency throughout. Bounded scratch
    // storage avoids allocation (and therefore partial mutation on failure).
    VertexSet red_common{}, blue_common{};
    for (int word = 0; word < words_; ++word) {
        red_common[word] = red_[u * words_ + word] & red_[v * words_ + word];
        blue_common[word] = blue_[u * words_ + word] & blue_[v * words_ + word];
    }
    const bool old = has_edge(u, v);
    std::array<int, K4_MAX_ORDER> common;
    common.fill(-1);
    for (int x = 0; x < order_; ++x) {
        if (x == u || x == v) continue;
        if ((red_common[x / word_bits] >> (x % word_bits)) & 1) common[x] = 1;
        if ((blue_common[x / word_bits] >> (x % word_bits)) & 1) common[x] = 0;
        for (int center : {u, v}) {
            int other = center == u ? v : u;
            bool color = has_edge(other, x);
            const auto& rows = color ? red_ : blue_;
            const auto& pair = color ? red_common : blue_common;
            Count triples = 0;
            for (int word = 0; word < words_; ++word)
                triples += __builtin_popcountll(pair[word] & rows[x * words_ + word]);
            Count magnitude = clique_coefficient * triples + (color ? 0 : triangle_coefficient);
            add_cached_delta(center, x, old == has_edge(center, x) ? magnitude : -magnitude);
        }
    }
    for (int x = 0; x < order_; ++x) {
        if (common[x] >= 0) {
            for (int y = x + 1; y < order_; ++y)
                if (common[x] == common[y]) add_cached_delta(x, y, old == has_edge(x, y) ? clique_coefficient : -clique_coefficient);
        }
    }
    cached_[u * order_ + v] = cached_[v * order_ + u] = -cached_[u * order_ + v];
}

void Graph::add_cached_delta(int u, int v, Count change) noexcept {
    cached_[u * order_ + v] += change;
    cached_[v * order_ + u] += change;
}

bool Graph::has_edge(int u, int v) const noexcept {
    return (red_[u * words_ + v / word_bits] >> (v % word_bits)) & 1;
}
} // namespace
