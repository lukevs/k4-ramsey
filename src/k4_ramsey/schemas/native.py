"""Exact C ABI layouts from native/search.h (not JSON/Pydantic records).

ctypes needs fixed-width, contiguous C fields. The public Python count record is
validated separately by schemas.verification.Counts.
"""

import ctypes as C


class NativeCounts(C.Structure):
    _fields_ = [
        (name, C.c_int64)
        for name in ("red_edges", "blue_triangles", "red_k4", "blue_k4", "numerator")
    ]


class NativeFlip(C.Structure):
    _fields_ = [(name, C.c_int64) for name in ("u", "v", "delta")]


class NativeStar(C.Structure):
    _fields_ = [
        (name, C.c_int64)
        for name in ("center", "blue_neighbor", "red_neighbor", "delta")
    ]
