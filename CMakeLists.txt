cmake_minimum_required(VERSION 2.8.12)

if (POLICY CMP0048)
    cmake_policy(SET CMP0048 NEW)
endif()

project(pvxmlgen)

set(PVXMLGEN_MASTER_PROJECT OFF)
if (CMAKE_CURRENT_SOURCE_DIR STREQUAL CMAKE_SOURCE_DIR)
    set(PVXMLGEN_MASTER_PROJECT ON)
endif()

option(PVXMLGEN_BUILD_EXAMPLE "Build Example" ${PVXMLGEN_MASTER_PROJECT})

set(Python_ADDITIONAL_VERSIONS 3.7 3.6 3.5 3.4)
find_package(PythonInterp REQUIRED)

set(PVXMLGEN_SCRIPT_PATH "${CMAKE_CURRENT_LIST_DIR}/pvxmlgen.py" CACHE INTERNAL "")
set(PYTHON_EXECUTABLE ${PYTHON_EXECUTABLE} CACHE INTERNAL "")

function(pvxmlgen_generate target)
    cmake_parse_arguments(ARG "" "INPUT;OUTPUT" "" ${ARGN})

    if (NOT IS_ABSOLUTE ${ARG_INPUT})
        set(ARG_INPUT "${CMAKE_CURRENT_SOURCE_DIR}/${ARG_INPUT}")
    endif()
    if (NOT IS_ABSOLUTE ${ARG_OUTPUT})
        set(ARG_OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/${ARG_OUTPUT}")
    endif()

    add_custom_command(
        OUTPUT ${ARG_OUTPUT}
        DEPENDS ${ARG_INPUT}
        COMMAND ${PYTHON_EXECUTABLE} ${PVXMLGEN_SCRIPT_PATH} ${ARG_INPUT} ${ARG_OUTPUT}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR})

    add_custom_target(${target}_xml DEPENDS ${ARG_OUTPUT})
    add_dependencies(${target} ${target}_xml)
endfunction()

if (PVXMLGEN_BUILD_EXAMPLE)
    add_subdirectory(example)
endif()
