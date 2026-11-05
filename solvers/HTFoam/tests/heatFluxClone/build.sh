#!/usr/bin/env bash
# No permissive unresolved-symbol flags; all output goes into a fresh directory.
set -eu
: "${WM_PROJECT_DIR:?Source OpenFOAM 10 in bash first}"
test_dir=$(cd "$(dirname "$0")" && pwd)
repo_dir=$(cd "$test_dir/../../../.." && pwd)
clone_run=${1:?Supply a fresh absolute run directory}
case "$clone_run" in /*) ;; *) echo 'An absolute run directory is required' >&2; exit 1;; esac
if [ -e "$clone_run" ]; then echo "Refusing to overwrite $clone_run" >&2; exit 1; fi
bc_source=${HEATFLUX_BC_SOURCE:-$repo_dir/libraries/BoundaryConditions}
mkdir -p "$clone_run/source/BoundaryConditions/Make" "$clone_run/source/probe/Make" "$clone_run/bin" "$clone_run/lib"
for part in HydrothermalHeatFlux HydrothermalMassFluxPressure SubmarinePressure noFlux; do
    cp -R "$bc_source/$part" "$clone_run/source/BoundaryConditions/"
done
cp "$bc_source"/Make/{files,options} "$clone_run/source/BoundaryConditions/Make/"
# Unit-test this BC independently. HEATFLUX_FULL_LIBRARY=1 retains the full
# integration build, exercised by tests/boundaryClones.
if [ "${HEATFLUX_FULL_LIBRARY:-0}" != 1 ]; then
    printf 'HydrothermalHeatFlux/HydrothermalHeatFluxFvPatchScalarField.C\n\nLIB=$(FOAM_USER_LIBBIN)/libHydrothermalBoundaryConditions\n' > "$clone_run/source/BoundaryConditions/Make/files"
fi
cp "$test_dir/probe/cloneProbe.C" "$clone_run/source/probe/"
cp "$test_dir"/probe/Make/{files,options} "$clone_run/source/probe/Make/"
export FOAM_USER_APPBIN="$clone_run/bin" FOAM_USER_LIBBIN="$clone_run/lib"
export CLONE_HEADER_DIR="$clone_run/source/BoundaryConditions/HydrothermalHeatFlux"
case "$(uname -s)" in
    Darwin) export CLONE_LINK_FLAGS='-Wl,-undefined,error';;
    Linux) export CLONE_LINK_FLAGS='-Wl,--no-allow-shlib-undefined';;
    *) echo 'Unsupported test platform' >&2; exit 1;;
esac
(cd "$clone_run/source/BoundaryConditions" && wmake libso) > "$clone_run/log.library-build" 2>&1
(cd "$clone_run/source/probe" && wmake) > "$clone_run/log.probe-build" 2>&1
printf 'Strict-linked clone probe: %s\n' "$clone_run/bin/heatFluxCloneProbe"
