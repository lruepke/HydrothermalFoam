# xThermo exports its headers and GSL dependencies through the package target.
# The shell variable xThermo_DIR denotes an installation prefix; CMake's
# xThermo_DIR cache entry denotes the directory containing xThermoConfig.cmake.
set(HTFOAM_XTHERMO_ROOT "$ENV{xThermo_DIR}" CACHE PATH "xThermo installation prefix")
find_package(xThermo CONFIG REQUIRED
    HINTS "${HTFOAM_XTHERMO_ROOT}/lib/cmake/xThermo")
message(STATUS "xThermo package: ${xThermo_DIR}")
