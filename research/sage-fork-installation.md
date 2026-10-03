# FlagAlgebraToolbox installation — 2026-09-29

User explicitly authorized installation. Build completed successfully and the
exact Mantel smoke test passed (exit 0, bound 1/2). The six-vertex K4 reproduction
also completed successfully (exit 0).

## K4 reproduction result

- Numerical lower bound: 0.028750917255328634.
- Toolbox exact-rounded rational bound: approximately 0.02875091866722224.
- Our previous independently checked rational certificate: 0.028750881.
- The toolbox rounded value is about 3.77e-8 stronger than that certificate,
  and near our previous numerical optimum (~0.0287509251).
- This reproduces the small six-vertex relaxation to numerical accuracy;
  it does not improve the published ~0.0296 lower bound.
- Exact rounding is reported by the toolbox; its certificate has not been
  exported and checked with our independent checker.
- Full output and exact fraction: `../reports/toolbox-reproduction-001/run.log`.

- Container: `flag-sage`, Ubuntu 24.04, native ARM64.
- Persistent named volume: `flag-sage-home`, mounted at `/home`.
- Build user: `researcher` (non-root).
- Source/build directory: `/home/researcher/flag-sage`.
- Repository: https://github.com/bodnalev/sage.git
- Branch: `flag-algebras`.
- Revision: `6d8c7d2ecfa8b27d8373d1987678dc34c84ed45a`.
- Configured using `make configure`, then `./configure`.
- Build command: `make -j4 build`.
- Main build log: `/home/researcher/build.log` inside the container.
- Configuration and apt logs: `/home/researcher/*dependencies.log`,
  `configure*.log`, `extra-libraries.log`.
- Prepared reproduction: `/home/researcher/reproduce_toolbox.sage`.

The minimal recipe needed additional Boost, compression and Python development
libraries. Additional Ubuntu mathematical libraries were installed to reduce
source compilation. Some are too old for this fork, which builds newer versions.
BRiAl Ubuntu packages were unavailable and were omitted from the apt list.

The first build stopped after 31m30s at a missing `csdpy-0.1.tar.gz`
download (203 installed-package markers). Upstream replaced the archive on its
moving master branch. Recovered the original from author commit
`9400b9b55d28abf179b84b7c263e774982a1db83`, under
`https://raw.githubusercontent.com/bodnalev/csdpy/9400b9b55d28abf179b84b7c263e774982a1db83/dist/csdpy-0.1.tar.gz`.
Its SHA256 matches the fork's existing pinned checksum exactly:
`e84c13ba5994c3fbfd1fef36a60ed05a3a382b7b4402f2968c77afcc276779f2`.
Saved in the Sage `upstream/` cache; no version or checksum changes needed.
Resumed `make -j4 build`, logging to `/home/researcher/build-resume.log`.
Verification remains pending.

The resumed build then failed compiling csdpy because its setup.py passes
Intel-only `-m64` on ARM64. Added a persistent Sage package patch at
`build/pkgs/csdpy/patches/arm-compiler-flags.patch` inside the container:
import `platform` and pass `-m64` only on x86_64/AMD64. Solver code is unchanged.
Resumed again, with log `/home/researcher/build-resume-arm.log`.

This final build completed in 12m47s. The prepared `toolbox_smoke.sage` ran
successfully through CSDP and exact rounding, printing
`PASS: exact Mantel bound 1/2`. K4 reproduction output is being written to
`/home/researcher/reproduce-toolbox.log` inside the container.

Open an interactive Sage session after successful installation:

    docker exec -it -u researcher -w /home/researcher/flag-sage flag-sage ./sage

Run the prepared K4 reproduction after the smoke test passes:

    docker exec -u researcher -w /home/researcher/flag-sage \
      -e OPENBLAS_NUM_THREADS=1 -e OMP_NUM_THREADS=1 flag-sage \
      ./sage /home/researcher/reproduce_toolbox.sage

The volume stores the source, compiled installation and researcher files.
System packages are installed in the persistent container layer. Recreating
the container from a plain Ubuntu image requires reinstalling those packages,
even if the `/home` volume is reused. Do not delete/recreate the container
as a routine way to restart it; use `docker start flag-sage` if stopped.
