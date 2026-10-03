#include "../../native/search.h"

#include <cassert>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <new>
#include <thread>
#include <vector>

// Test-only failure injection, compiled into this executable, not the library.
thread_local int allocation_countdown = -1;
void* operator new(std::size_t size) {
    if (allocation_countdown == 0) throw std::bad_alloc();
    if (allocation_countdown > 0) --allocation_countdown;
    if (void* ptr = std::malloc(size ? size : 1)) return ptr;
    throw std::bad_alloc();
}
void operator delete(void* ptr) noexcept { std::free(ptr); }
void operator delete(void* ptr, std::size_t) noexcept { std::free(ptr); }

void test_invalid_inputs();
void test_allocation_failures();
void test_literal_counts_and_deltas();
void test_word_boundaries();
void test_thread_local_errors();

int main() {
    test_invalid_inputs();
    test_allocation_failures();
    test_literal_counts_and_deltas();
    test_word_boundaries();
    test_thread_local_errors();
    std::cout << "Native ABI, allocation-failure, literal-count, and boundary tests passed\n";
}

void test_invalid_inputs() {
    uint8_t matrix[9] = {};
    for (int n : {0, -1, 1025}) {
        assert(k4_new(n, matrix) == nullptr);
        assert(k4_error_code() == K4_INVALID_ARGUMENT);
    }
    assert(k4_new(3, nullptr) == nullptr);
    for (auto changed : {0, 1}) {
        matrix[changed] = 1;
        assert(k4_new(3, matrix) == nullptr); // diagonal or asymmetry
        matrix[changed] = 0;
    }
    matrix[1] = matrix[3] = 2;
    assert(k4_new(3, matrix) == nullptr);
    matrix[1] = matrix[3] = 0;
    void* graph = k4_new(3, matrix);
    assert(graph && k4_error_code() == K4_OK);
    k4_flip(graph, -1, 1);
    assert(k4_error_code() == K4_INVALID_ARGUMENT);
    k4_delta(graph, 0, 3);
    assert(k4_error_code() == K4_INVALID_ARGUMENT);
    k4_flip(graph, 0, 0);
    assert(k4_error_code() == K4_INVALID_ARGUMENT);
    k4_cached_delta(graph, 0, 1);
    assert(k4_error_code() == K4_INVALID_ARGUMENT);
    K4Flip flip{9, 9, 9};
    assert(!k4_find_best_flip(graph, &flip) && flip.u == 9);
    assert(!k4_count_subgraphs(graph, nullptr));
    assert(!k4_enable_cache(nullptr));
    k4_export(graph, nullptr);
    assert(k4_error_code() == K4_INVALID_ARGUMENT);
    int us[] = {0, 0}, vs[] = {1, 9};
    int64_t deltas[] = {123, 456};
    k4_deltas(graph, us, vs, 2, deltas);
    assert(k4_error_code() == K4_INVALID_ARGUMENT && deltas[0] == 123 && deltas[1] == 456);
    k4_deltas(graph, nullptr, nullptr, -1, nullptr);
    assert(k4_error_code() == K4_INVALID_ARGUMENT);
    k4_deltas(graph, nullptr, nullptr, 0, nullptr);
    assert(k4_error_code() == K4_OK);
    assert(k4_enable_cache(graph));
    K4Star star{9, 9, 9, 9};
    for (int limit : {-1, 0, 1025}) {
        assert(!k4_find_best_star(graph, limit, &star));
        assert(star.center == 9 && k4_error_code() == K4_INVALID_ARGUMENT);
    }
    int expiry[9] = {};
    assert(!k4_find_allowed_flip(graph, expiry, -1, 0, &flip));
    assert(!k4_find_allowed_flip(graph, nullptr, 0, 0, &flip));
    uint8_t after[9];
    k4_export(graph, after);
    assert(std::memcmp(matrix, after, sizeof(matrix)) == 0);
    assert(k4_error_code() == K4_OK); // success clears a preceding error
    k4_free(graph);
    k4_free(nullptr);
    assert(k4_error_code() == K4_OK);
}

void test_allocation_failures() {
    uint8_t matrix[9] = {};
    for (int allocation : {0, 1, 2}) {
        allocation_countdown = allocation;
        void* graph = k4_new(3, matrix);
        allocation_countdown = -1;
        assert(graph == nullptr && k4_error_code() == K4_OUT_OF_MEMORY);
    }
    void* graph = k4_new(3, matrix);
    allocation_countdown = 0;
    assert(!k4_enable_cache(graph));
    allocation_countdown = -1;
    assert(k4_error_code() == K4_OUT_OF_MEMORY);
    k4_cached_delta(graph, 0, 1);
    assert(k4_error_code() == K4_INVALID_ARGUMENT); // no partial cache was published
    assert(k4_enable_cache(graph));
    K4Counts before{}, after{};
    assert(k4_count_subgraphs(graph, &before));
    K4Star star{9, 9, 9, 9};
    allocation_countdown = 0;
    assert(!k4_find_best_star(graph, 2, &star));
    allocation_countdown = -1;
    assert(k4_error_code() == K4_OUT_OF_MEMORY && star.center == 9);
    assert(k4_count_subgraphs(graph, &after));
    assert(before.numerator == after.numerator);
    // A cached flip is now allocation-free, even when every allocation would fail.
    auto delta = k4_delta(graph, 0, 1);
    allocation_countdown = 0;
    k4_flip(graph, 0, 1);
    assert(k4_error_code() == K4_OK);
    allocation_countdown = -1;
    assert(k4_count_subgraphs(graph, &after));
    assert(after.numerator == before.numerator + delta);
    assert(k4_cached_delta(graph, 0, 1) == -delta);
    k4_free(graph);
}

int64_t count_literal(const uint8_t* matrix, int n) {
    int64_t total = 0;
    for (int a = 0; a < n; ++a) for (int b = 0; b < n; ++b)
        for (int c = 0; c < n; ++c) for (int d = 0; d < n; ++d) {
            const auto color = matrix[a * n + b];
            total += matrix[a * n + c] == color && matrix[a * n + d] == color
                && matrix[b * n + c] == color && matrix[b * n + d] == color
                && matrix[c * n + d] == color;
        }
    return total;
}

void test_literal_counts_and_deltas() {
    for (int mask = 0; mask < 64; ++mask) {
        uint8_t matrix[16] = {};
        int bit = 0;
        for (int i = 0; i < 4; ++i) for (int j = i + 1; j < 4; ++j)
            matrix[i * 4 + j] = matrix[j * 4 + i] = (mask >> bit++) & 1;
        void* graph = k4_new(4, matrix);
        assert(graph && k4_enable_cache(graph));
        K4Counts counts{};
        assert(k4_count_subgraphs(graph, &counts));
        assert(counts.numerator == count_literal(matrix, 4));
        int64_t legacy[5];
        k4_counts(graph, legacy);
        assert(legacy[0] == counts.red_edges && legacy[4] == counts.numerator);
        for (int u = 0; u < 4; ++u) for (int v = u + 1; v < 4; ++v) {
            const auto change = k4_delta(graph, u, v);
            assert(change == k4_cached_delta(graph, u, v));
            k4_flip(graph, u, v);
            matrix[u * 4 + v] ^= 1; matrix[v * 4 + u] ^= 1;
            assert(count_literal(matrix, 4) == counts.numerator + change);
            for (int i = 0; i < 4; ++i) for (int j = i + 1; j < 4; ++j)
                assert(k4_cached_delta(graph, i, j) == k4_delta(graph, i, j));
            k4_flip(graph, u, v);
            matrix[u * 4 + v] ^= 1; matrix[v * 4 + u] ^= 1;
        }
        k4_free(graph);
    }
}

void test_word_boundaries() {
    for (int n : {1, 63, 64, 65, 1024}) {
        std::vector<uint8_t> matrix(n * n, 0), exported(n * n);
        void* graph = k4_new(n, matrix.data());
        assert(graph);
        if (n > 1) {
            assert(k4_delta(graph, 0, n - 1) < 0);
            k4_flip(graph, 0, n - 1);
            matrix[n - 1] = matrix[(n - 1) * n] = 1;
        }
        k4_export(graph, exported.data());
        assert(exported == matrix);
        k4_free(graph);
    }
}

void test_thread_local_errors() {
    k4_delta(nullptr, 0, 1);
    assert(k4_error_code() == K4_INVALID_ARGUMENT);
    std::thread other([] {
        assert(k4_error_code() == K4_OK);
        k4_free(nullptr);
        assert(k4_error_code() == K4_OK);
    });
    other.join();
    assert(k4_error_code() == K4_INVALID_ARGUMENT);
}
