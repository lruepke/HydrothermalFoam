cmake_minimum_required(VERSION 3.20 FATAL_ERROR)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
set(CMAKE_XCODE_GENERATE_SCHEME TRUE)
project(HTFoam LANGUAGES CXX C)

include(OpenFOAM)
include(xThermo)
set(Solver HTFoam)

#             Include path configuration, similar to that in Make/options
include_directories(
        ${CMAKE_CURRENT_SOURCE_DIR}
        # ${OpenFOAM_SRC}/thermophysicalModels/basic/lnInclude
        # ${CMAKE_CURRENT_SOURCE_DIR}/../../libraries/ThermoModels/basic/hydroThermo
        ${xThermo_INCLUDE}
        )
# =====================================================================================
set(TARGET_NAME test_${Solver})
add_executable(${TARGET_NAME} ${Solver}.C)
# dynamic link
#target_link_libraries(${TARGET_NAME} ${Libs_Mandatory} fvOptions sampling meshTools fluidThermophysicalModels specie ${xThermo_STATIC} ${GSL_LIBRARIES_STATIC})
target_link_libraries(${TARGET_NAME} ${Libs_Mandatory} ${xThermo_STATIC})
set_target_properties(${TARGET_NAME} PROPERTIES
        OUTPUT_NAME ${Solver}
#        RUNTIME_OUTPUT_DIRECTORY $ENV{FOAM_USER_APPBIN}
        )


