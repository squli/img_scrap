cmake_minimum_required(VERSION 3.10)

# Set project name
project(MathClient)

# Define the executable
add_executable(MathClient MathClient.cpp)

# Link MathLibrary
target_link_libraries(MathClient MathLibrary)

# Specify the include directories for MathLibrary
target_include_directories(MathClient PRIVATE ../MathLibrary)