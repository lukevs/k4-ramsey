"""The ctypes boundary must turn native failures into Python exceptions."""
import ctypes as C
import unittest

from k4_ramsey.engine import Graph, load_native_library, make_certificate
from k4_ramsey.schemas.native import NativeCounts, NativeFlip, NativeStar


class NativeBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.lib = load_native_library()
        self.graph = Graph(make_certificate(["000", "000", "000"]))
        self.addCleanup(self.graph.close)

    def test_native_nulls_and_matrix_validation_raise(self):
        with self.assertRaisesRegex(ValueError, "null graph"):
            self.lib.k4_delta(None, 0, 1)
        with self.assertRaisesRegex(ValueError, "null adjacency"):
            self.lib.k4_new(3, None)
        malformed = (C.c_uint8 * 9)(0, 1, 0, 0, 0, 0, 0, 0, 0)
        with self.assertRaisesRegex(ValueError, "symmetric"):
            self.lib.k4_new(3, malformed)
        with self.assertRaisesRegex(ValueError, "order"):
            self.lib.k4_new(1025, malformed)

    def test_bad_mutation_is_rejected_without_changes(self):
        before = self.graph.export_certificate()
        for endpoints in [(-1, 0), (0, 3), (1, 1)]:
            with self.subTest(endpoints=endpoints), self.assertRaises(ValueError):
                self.lib.k4_flip(self.graph.ptr, *endpoints)
        self.assertEqual(self.graph.export_certificate(), before)
        for endpoints in [(True, 1), (0.5, 1), (0, "1")]:
            with self.subTest(endpoints=endpoints), self.assertRaises(ValueError):
                self.graph.flip(*endpoints)

    def test_cache_preconditions_and_named_results(self):
        with self.assertRaisesRegex(ValueError, "cache"):
            self.lib.k4_find_best_flip(self.graph.ptr, C.byref(NativeFlip()))
        self.graph.enable_cache()
        out = NativeCounts()
        self.lib.k4_count_subgraphs(self.graph.ptr, C.byref(out))
        self.assertEqual(out.numerator, 81)
        self.assertEqual(out.numerator, self.graph.count_subgraphs()["numerator"])
        with self.assertRaisesRegex(ValueError, "per_color"):
            self.lib.k4_find_best_star(self.graph.ptr, -1, C.byref(NativeStar()))
        # Query after an error succeeds; stale error state is cleared per call.
        self.assertIsNotNone(self.graph.find_best_cached_flip())

    def test_invalid_batch_does_not_write_partial_results(self):
        us, vs = (C.c_int * 2)(0, 0), (C.c_int * 2)(1, 5)
        output = (C.c_int64 * 2)(123, 456)
        with self.assertRaises(ValueError):
            self.lib.k4_deltas(self.graph.ptr, us, vs, 2, output)
        self.assertEqual(list(output), [123, 456])
        self.assertEqual(self.graph.calculate_deltas([]), [])

    def test_closed_graph_fails_without_native_dereference(self):
        self.graph.close()
        with self.assertRaises(ValueError):
            self.graph.count_subgraphs()
        with self.assertRaises(ValueError):
            self.graph.flip(0, 1)
