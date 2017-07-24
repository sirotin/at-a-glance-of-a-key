# minimal CMakeLists.txt for the AWS SDK for C++

cmake_minimum_required(VERSION 2.8)
set (CMAKE_CXX_STANDARD 11)
#set (CMAKE_BUILD_TYPE Debug)

project(benchmark)

# -Daws-sdk-cpp_DIR=/path/to/sdk_build
find_package(aws-sdk-cpp)
add_definitions(-DUSE_IMPORT_EXPORT)

file (GLOB SOURCES "src/*.h" "src/*.cpp" "src/*.hpp")

add_executable(benchmark ${SOURCES})
target_link_libraries(benchmark aws-cpp-sdk-sqs)

