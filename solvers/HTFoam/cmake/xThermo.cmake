# Basic configuration of xThermo package in cmake

# Check valid xThermo environment
set(xThermo_DIR "$ENV{xThermo_DIR}" CACHE FILEPATH "Path of xThermo library contains include, lib")

if(EXISTS ${xThermo_DIR})
	MESSAGE(STATUS "xThermo is found: " ${xThermo_DIR})
else()
	message(FATAL_ERROR "The xThermo package is not found, please set its path using argument -DxThermo_DIR=path_xThermo, which contains include, SHARED, STATIC")
endif()
set(xThermo_INCLUDE "")
list(APPEND xThermo_INCLUDE ${xThermo_DIR}/include )
set(xThermo_STATIC "")
list(APPEND xThermo_STATIC
		${xThermo_DIR}/STATIC/${CMAKE_SHARED_LIBRARY_PREFIX}xThermal${CMAKE_STATIC_LIBRARY_SUFFIX}
		${xThermo_DIR}/STATIC/${CMAKE_SHARED_LIBRARY_PREFIX}gsl${CMAKE_STATIC_LIBRARY_SUFFIX}
		${xThermo_DIR}/STATIC/${CMAKE_SHARED_LIBRARY_PREFIX}gslcblas${CMAKE_STATIC_LIBRARY_SUFFIX}
		#${xThermo_DIR}/STATIC/${CMAKE_SHARED_LIBRARY_PREFIX}CoolProp${CMAKE_STATIC_LIBRARY_SUFFIX}
		)
set(xThermo_SHARED ${xThermo_DIR}/SHARED/${CMAKE_SHARED_LIBRARY_PREFIX}xThermal${CMAKE_SHARED_LIBRARY_SUFFIX})
set(xThermo_STATIC_PAR ${xThermo_DIR}/STATIC/${CMAKE_SHARED_LIBRARY_PREFIX}xThermo_par${CMAKE_STATIC_LIBRARY_SUFFIX})
set(xThermo_SHARED_PAR ${xThermo_DIR}/SHARED/${CMAKE_SHARED_LIBRARY_PREFIX}xThermo_par${CMAKE_SHARED_LIBRARY_SUFFIX})

#if(EXISTS ${xThermo_SHARED})
#	message(STATUS "xThermo shared lib found: " ${xThermo_SHARED})
#else()
#	message(WARNING "xThermo shared lib doesn't exist: " ${xThermo_SHARED})
#endif()
#if(EXISTS ${xThermo_STATIC})
#	message(STATUS "xThermo static lib found: " ${xThermo_STATIC})
#else()
#	message(WARNING "xThermo static lib doesn't exist: " ${xThermo_STATIC})
#endif()
#if(EXISTS ${xThermo_STATIC_PAR})
#	message(STATUS "xThermo static lib(parallel version) found: " ${xThermo_STATIC_PAR})
#else()
#	message(WARNING "xThermo static lib(parallel version) doesn't exist: " ${xThermo_STATIC_PAR})
#endif()
#if(EXISTS ${xThermo_SHARED_PAR})
#	message(STATUS "xThermo shared lib(parallel version) found: " ${xThermo_SHARED_PAR})
#else()
#	message(WARNING "xThermo shared lib(parallel version) doesn't exist: " ${xThermo_SHARED_PAR})
#endif()
