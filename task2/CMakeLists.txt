cmake_minimum_required(VERSION 3.10)

set(CMAKE_CXX_STANDARD 17)
if (LINUX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall")
	set(CMAKE_CXX_COMPILER g++-9)
	set(CMAKE_C_COMPILER gcc-9)
else()
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2 -Wall")
endif (LINUX)

project(MathProject LANGUAGES CXX)

add_subdirectory(MathLibrary MathLibrary)
add_subdirectory(MathClient MathClient)