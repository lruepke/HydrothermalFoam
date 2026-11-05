#!/usr/bin/env bash
# Build only in a fresh ignored run directory; preserve installed/review binaries.
set -eu
: "${WM_PROJECT_DIR:?Source OpenFOAM 10 in bash first}"
: "${xThermo_DIR:?Set xThermo_DIR to the reviewed installation prefix}"
tests_dir=$(cd "$(dirname "$0")" && pwd)
repo_dir=$(cd "$tests_dir/../../../.." && pwd)
conductivity_run=${1:?Supply a fresh absolute tests/conductivity/run-NAME directory}
case "$conductivity_run" in "$tests_dir"/run-*) ;; *) echo 'Use a run-NAME directory inside tests/conductivity' >&2; exit 1;; esac
if [ -e "$conductivity_run" ]; then echo "Refusing to overwrite $conductivity_run" >&2; exit 1; fi
mkdir -p "$conductivity_run/bin" "$conductivity_run/lib" "$conductivity_run/source/solver/Make" "$conductivity_run/source/BoundaryConditions/Make" "$conductivity_run/source/probe/Make"
cp "$repo_dir"/solvers/HTFoam/*.C "$repo_dir"/solvers/HTFoam/*.H "$conductivity_run/source/solver/"
cp "$repo_dir"/solvers/HTFoam/Make/{files,options} "$conductivity_run/source/solver/Make/"
for part in HydrothermalHeatFlux HydrothermalMassFluxPressure SubmarinePressure noFlux; do
    cp -R "$repo_dir/libraries/BoundaryConditions/$part" "$conductivity_run/source/BoundaryConditions/"
done
cp "$repo_dir"/libraries/BoundaryConditions/Make/{files,options} "$conductivity_run/source/BoundaryConditions/Make/"
cp "$tests_dir/probe/conductivityProbe.C" "$conductivity_run/source/probe/"
cp "$tests_dir"/probe/Make/{files,options} "$conductivity_run/source/probe/Make/"
export FOAM_USER_APPBIN="$conductivity_run/bin" FOAM_USER_LIBBIN="$conductivity_run/lib"
export HTFOAM_REVIEW_SRC="$conductivity_run/source/solver"
(cd "$conductivity_run/source/BoundaryConditions" && wmake libso) > "$conductivity_run/log.library-build" 2>&1
(cd "$conductivity_run/source/solver" && wmake) > "$conductivity_run/log.solver-build" 2>&1
(cd "$conductivity_run/source/probe" && wmake) > "$conductivity_run/log.probe-build" 2>&1
printf 'Isolated executables: %s\nIsolated library: %s\n' "$FOAM_USER_APPBIN" "$FOAM_USER_LIBBIN"
