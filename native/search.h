#ifndef K4_SEARCH_H
#define K4_SEARCH_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#define K4_NOEXCEPT noexcept
#else
#define K4_NOEXCEPT
#endif

enum { K4_MAX_ORDER = 1024 };
enum K4Error { K4_OK = 0, K4_INVALID_ARGUMENT = 1, K4_OUT_OF_MEMORY = 2, K4_INTERNAL_ERROR = 3 };

typedef struct K4Counts {
    int64_t red_edges, blue_triangles, red_k4, blue_k4, numerator;
} K4Counts;

/* A negative first vertex means no move; otherwise delta is an exact change. */
typedef struct K4Flip { int64_t u, v, delta; } K4Flip;
typedef struct K4Star { int64_t center, blue_neighbor, red_neighbor, delta; } K4Star;

/* Every operation clears this thread's previous error and contains exceptions.
 * Inspect the error immediately after a call; sentinel return values alone do
 * not distinguish a failure from a legitimate zero/no-move result.
 * These two queries do not clear the error and never allocate. */
int k4_error_code(void) K4_NOEXCEPT;
const char* k4_last_error(void) K4_NOEXCEPT;

/* Ownership: k4_new returns a handle owned by the caller; free it exactly once.
 * Handles must be live objects returned by k4_new. Buffers must have the lengths
 * stated here. Null pointers, dimensions, matrix values, indices, and cache
 * state are checked, but arbitrary dangling pointers/buffer sizes cannot be
 * discovered through this C ABI. Do not share a handle across concurrent calls.
 * matrix has n*n bytes, is symmetric/binary, and has a zero diagonal. */
void* k4_new(int n, const uint8_t* matrix) K4_NOEXCEPT;
void k4_free(void* graph) K4_NOEXCEPT;
void k4_flip(void* graph, int u, int v) K4_NOEXCEPT;
int64_t k4_delta(void* graph, int u, int v) K4_NOEXCEPT;
/* us, vs, and out have size entries. Empty batches may use null buffers. */
void k4_deltas(void* graph, const int* us, const int* vs, int size, int64_t* out) K4_NOEXCEPT;
/* out has n*n bytes. */
void k4_export(void* graph, uint8_t* out) K4_NOEXCEPT;
int k4_enable_cache(void* graph) K4_NOEXCEPT;
int64_t k4_cached_delta(void* graph, int u, int v) K4_NOEXCEPT;
void k4_cached_deltas(void* graph, const int* us, const int* vs, int size, int64_t* out) K4_NOEXCEPT;

/* Named-result interface. Returns 1 on success, 0 on failure. Output is left
 * unchanged on failure. Cache queries require k4_enable_cache first.
 * expiry has n*n signed-int entries; step >= 0; per_color is 1..K4_MAX_ORDER. */
int k4_count_subgraphs(void* graph, K4Counts* out) K4_NOEXCEPT;
int k4_find_best_flip(void* graph, K4Flip* out) K4_NOEXCEPT;
int k4_find_allowed_flip(void* graph, const int* expiry, int step, int64_t aspiration, K4Flip* out) K4_NOEXCEPT;
int k4_find_best_star(void* graph, int per_color, K4Star* out) K4_NOEXCEPT;

/* Legacy adapters: out has 5, 3, 3, or 4 int64_t entries respectively, in the
 * field order of the corresponding named result above. */
void k4_counts(void* graph, int64_t* out) K4_NOEXCEPT;
void k4_best_cached(void* graph, int64_t* out) K4_NOEXCEPT;
void k4_best_cached_allowed(void* graph, const int* expiry, int step, int64_t aspiration, int64_t* out) K4_NOEXCEPT;
void k4_best_cached_star(void* graph, int per_color, int64_t* out) K4_NOEXCEPT;

#ifdef __cplusplus
}
#endif
#undef K4_NOEXCEPT
#endif
