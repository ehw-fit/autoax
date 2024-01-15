cmake_minimum_required (VERSION 3.0)
set (CMAKE_CXX_STANDARD 11)
project (GAUSS)

find_package( OpenCV REQUIRED )
include_directories( ${OpenCV_INCLUDE_DIRS} )

file(GLOB libSource ../lib/*.c ../lib/*.cpp)

add_library(axlib STATIC ${libSource})

add_executable(axgauss axgauss.cpp lib.cpp similarity.cpp )
target_include_directories(axgauss PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../lib)
target_link_libraries( axgauss ${OpenCV_LIBS} axlib )
