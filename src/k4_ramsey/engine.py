"""Small ctypes interface: fast exact primitives, replaceable Python experiments."""

from __future__ import annotations

import ctypes as C
import sys
from pathlib import Path

from .artifacts import read_json
from .schemas.certificates import UnitCertificate
from .schemas.verification import Counts

ROOT = Path(__file__).resolve().parents[2]
TARGET = 10486266368
SEED_NUMERATOR = 10487165184
SEED = ROOT / "data/published_cayley_768.json"
_lib = None


class Graph:
    def __init__(self, data: dict):
        rows = validate_certificate(data)
        self.n = len(rows)
        self.lib = load_native_library()
        matrix = (C.c_uint8 * (self.n * self.n))(*(int(v) for r in rows for v in r))
        self.ptr = self.lib.k4_new(self.n, matrix)
        if not self.ptr:
            raise MemoryError("native graph allocation failed")
        self.cache_enabled = False

    def close(self):
        if getattr(self, "ptr", None):
            self.lib.k4_free(self.ptr)
            self.ptr = None

    def __del__(self):
        self.close()

    def validate_endpoints(self, u, v):
        if not self.ptr or not (0 <= u < self.n and 0 <= v < self.n and u != v):
            raise ValueError("invalid edge or closed graph")

    def calculate_delta(self, u: int, v: int) -> int:
        self.validate_endpoints(u, v)
        return self.lib.k4_delta(self.ptr, u, v)

    def flip(self, u: int, v: int):
        self.validate_endpoints(u, v)
        self.lib.k4_flip(self.ptr, u, v)

    def calculate_deltas(self, pairs: list[tuple[int, int]]) -> list[int]:
        for u, v in pairs:
            self.validate_endpoints(u, v)
        size = len(pairs)
        us, vs = (
            (C.c_int * size)(*(p[0] for p in pairs)),
            (C.c_int * size)(*(p[1] for p in pairs)),
        )
        out = (C.c_int64 * size)()
        self.lib.k4_deltas(self.ptr, us, vs, size, out)
        return list(out)

    def enable_cache(self):
        if not self.ptr:
            raise ValueError("closed graph")
        if not self.cache_enabled:
            if not self.lib.k4_enable_cache(self.ptr):
                raise MemoryError("native delta cache allocation failed")
            self.cache_enabled = True

    def calculate_cached_delta(self, u: int, v: int) -> int:
        self.validate_endpoints(u, v)
        self.enable_cache()
        return self.lib.k4_cached_delta(self.ptr, u, v)

    def calculate_cached_deltas(self, pairs: list[tuple[int, int]]) -> list[int]:
        for u, v in pairs:
            self.validate_endpoints(u, v)
        self.enable_cache()
        size = len(pairs)
        us, vs = (
            (C.c_int * size)(*(p[0] for p in pairs)),
            (C.c_int * size)(*(p[1] for p in pairs)),
        )
        out = (C.c_int64 * size)()
        self.lib.k4_cached_deltas(self.ptr, us, vs, size, out)
        return list(out)

    def find_best_cached_flip(self) -> tuple[int, int, int] | None:
        """Return (u,v,delta) minimizing the exact cached single-flip delta."""
        self.enable_cache()
        out = (C.c_int64 * 3)()
        self.lib.k4_best_cached(self.ptr, out)
        return None if out[0] < 0 else tuple(out)

    def find_best_cached_allowed(self, expiry, step: int, aspiration_delta: int):
        """Scan exact deltas with tabu expiry and strict aspiration.

        expiry is a persistent ctypes c_int[n*n] buffer owned by the caller;
        use symmetric entries. Allowed iff expiry<=step or delta<aspiration.
        """
        if (
            not isinstance(expiry, C.Array)
            or expiry._type_ is not C.c_int
            or len(expiry) != self.n * self.n
        ):
            raise ValueError("expiry must be a ctypes c_int[n*n] buffer")
        if type(step) is not int or not 0 <= step < 2**31:
            raise ValueError("step must be a nonnegative int32")
        if (
            type(aspiration_delta) is not int
            or not -(2**63) <= aspiration_delta < 2**63
        ):
            raise ValueError("aspiration_delta must be int64")
        self.enable_cache()
        out = (C.c_int64 * 3)()
        self.lib.k4_best_cached_allowed(self.ptr, expiry, step, aspiration_delta, out)
        return None if out[0] < 0 else tuple(out)

    def find_best_cached_star(self, per_color: int = 16):
        """Best strict shared-center red/blue swap in low-cost shortlists.

        Return (center,blue_neighbor,red_neighbor,joint_delta), or None.
        A shortlist is not an exhaustive star-neighborhood certificate.
        """
        if type(per_color) is not int or not 1 <= per_color <= 1024:
            raise ValueError("per_color must be 1..1024")
        self.enable_cache()
        out = (C.c_int64 * 4)()
        self.lib.k4_best_cached_star(self.ptr, per_color, out)
        return None if out[0] < 0 else tuple(out)

    def count_subgraphs(self) -> dict:
        if not self.ptr:
            raise ValueError("closed graph")
        out = (C.c_int64 * 5)()
        self.lib.k4_counts(self.ptr, out)
        return Counts(
            **dict(
                zip(
                    ("red_edges", "blue_triangles", "red_k4", "blue_k4", "numerator"),
                    out,
                )
            )
        ).model_dump(mode="json", by_alias=True, exclude_none=True)

    def export_certificate(self) -> dict:
        if not self.ptr:
            raise ValueError("closed graph")
        out = (C.c_uint8 * (self.n * self.n))()
        self.lib.k4_export(self.ptr, out)
        return make_certificate(
            [
                "".join(str(out[i * self.n + j]) for j in range(self.n))
                for i in range(self.n)
            ]
        )

    # Legacy method names used by historical experiments.
    counts = count_subgraphs
    endpoints = validate_endpoints
    delta = calculate_delta
    deltas = calculate_deltas
    cached_delta = calculate_cached_delta
    cached_deltas = calculate_cached_deltas
    best_cached_flip = find_best_cached_flip
    best_cached_allowed = find_best_cached_allowed
    best_cached_star = find_best_cached_star
    export = export_certificate


def read_certificate(path: Path) -> dict:
    """Read a strict certificate while preserving the public dictionary protocol."""
    return UnitCertificate.model_validate(read_json(path)).model_dump(
        mode="json", by_alias=True, exclude_none=True
    )


def make_certificate(rows: list[str]) -> dict:
    return dict(
        schema="weighted-two-color-blowup-v1", weights=[1] * len(rows), red_rows=rows
    )


def validate_certificate(data: dict) -> list[str]:
    """Validate the unit-weight search contract at the native boundary."""
    return UnitCertificate.model_validate(data).red_rows


def load_native_library():
    global _lib
    if _lib is None:
        _lib = C.CDLL(str(locate_native_library()))
        specs = {
            "k4_new": ([C.c_int, C.POINTER(C.c_uint8)], C.c_void_p),
            "k4_free": ([C.c_void_p], None),
            "k4_flip": ([C.c_void_p, C.c_int, C.c_int], None),
            "k4_delta": ([C.c_void_p, C.c_int, C.c_int], C.c_int64),
            "k4_counts": ([C.c_void_p, C.POINTER(C.c_int64)], None),
            "k4_deltas": (
                [
                    C.c_void_p,
                    C.POINTER(C.c_int),
                    C.POINTER(C.c_int),
                    C.c_int,
                    C.POINTER(C.c_int64),
                ],
                None,
            ),
            "k4_export": ([C.c_void_p, C.POINTER(C.c_uint8)], None),
            "k4_enable_cache": ([C.c_void_p], C.c_int),
            "k4_cached_delta": ([C.c_void_p, C.c_int, C.c_int], C.c_int64),
            "k4_cached_deltas": (
                [
                    C.c_void_p,
                    C.POINTER(C.c_int),
                    C.POINTER(C.c_int),
                    C.c_int,
                    C.POINTER(C.c_int64),
                ],
                None,
            ),
            "k4_best_cached": ([C.c_void_p, C.POINTER(C.c_int64)], None),
            "k4_best_cached_allowed": (
                [
                    C.c_void_p,
                    C.POINTER(C.c_int),
                    C.c_int,
                    C.c_int64,
                    C.POINTER(C.c_int64),
                ],
                None,
            ),
            "k4_best_cached_star": ([C.c_void_p, C.c_int, C.POINTER(C.c_int64)], None),
        }
        for name, (args, result) in specs.items():
            fn = getattr(_lib, name)
            fn.argtypes, fn.restype = args, result
    return _lib


def locate_native_library() -> Path:
    """Locate the prebuilt engine; compilation belongs to the justfile."""
    output = (
        ROOT / "build" / ("libk4.dylib" if sys.platform == "darwin" else "libk4.so")
    )
    if not output.is_file():
        raise RuntimeError("Native engine is not built; run just runner-build")
    return output


# Compatibility aliases for historical research scripts.
certificate = make_certificate
library = load_native_library
native_library_path = locate_native_library

load = read_certificate
validate = validate_certificate
