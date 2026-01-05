set(LIBNAME HydrothermalBoundaryConditions)
#             Include path configuration, similar to that in Make/options
include_directories(${OpenFOAM_SRC}/finiteVolume/lnInclude
                    ${CMAKE_CURRENT_SOURCE_DIR}/HydrothermalMassFluxPressure
                    ${CMAKE_CURRENT_SOURCE_DIR}/HydrothermalHeatFlux
                    ${CMAKE_CURRENT_SOURCE_DIR}/SubmarinePressure
                    ${CMAKE_CURRENT_SOURCE_DIR}/noFlux
                    )
# =====================================================================================
list(APPEND src_lib HydrothermalMassFluxPressure/HydrothermalMassFluxPressureFvPatchScalarField.C 
                    HydrothermalHeatFlux/HydrothermalHeatFluxFvPatchScalarField.C
                    SubmarinePressure/submarinePressureFvPatchScalarField.C
                    noFlux/noFluxFvPatchScalarField.C
                    )
add_library(${LIBNAME} SHARED ${src_lib})
# dynamic link
target_link_libraries(${LIBNAME} ${Libs_Mandatory} )
# set_target_properties(${Solver} PROPERTIES RUNTIME_OUTPUT_DIRECTORY $ENV{FOAM_USER_APPBIN})
set_target_properties(${LIBNAME} PROPERTIES
        #   OUTPUT_NAME ${LIB_NAME}
          LIBRARY_OUTPUT_DIRECTORY $ENV{FOAM_USER_LIBBIN}
          ARCHIVE_OUTPUT_DIRECTORY $ENV{FOAM_USER_LIBBIN}
          )

# ======================= Message out ===========================
message(STATUS "Configuration type: " ${CMAKE_CONFIGURATION_TYPES})
