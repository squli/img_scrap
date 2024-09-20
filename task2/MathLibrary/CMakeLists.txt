cmake_minimum_required(VERSION 3.10)

# Set project name
project(MathLibrary)

# Define the static library
add_library(MathLibrary STATIC MathLibrary.cpp)

# Specify the include directories
target_include_directories(MathLibrary PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})