#!/usr/bin/env bash
# Build the complete production library and both clone probes in isolation.
set -eu
: "${WM_PROJECT_DIR:?Source OpenFOAM 10 in bash first}"
test_dir=$(cd "$(dirname "$0")" && pwd)
clone_run=${1:?Supply a fresh absolute run directory}
HEATFLUX_FULL_LIBRARY=1 bash "$test_dir/../heatFluxClone/build.sh" "$clone_run"
mkdir -p "$clone_run/source/pressureProbe/Make"
cp "$test_dir/probe/pressureCloneProbe.C" "$clone_run/source/pressureProbe/"
cp "$test_dir"/probe/Make/{files,options} "$clone_run/source/pressureProbe/Make/"
export FOAM_USER_APPBIN="$clone_run/bin" FOAM_USER_LIBBIN="$clone_run/lib"
export CLONE_HEADER_DIR="$clone_run/source/BoundaryConditions/HydrothermalHeatFlux"
case "$(uname -s)" in
    Darwin) export CLONE_LINK_FLAGS='-Wl,-undefined,error';;
    Linux) export CLONE_LINK_FLAGS='-Wl,--no-allow-shlib-undefined';;
esac
(cd "$clone_run/source/pressureProbe" && wmake) > "$clone_run/log.pressure-probe-build" 2>&1
printf 'Complete library and strict-linked pressure probe: %s\n' "$clone_run"
