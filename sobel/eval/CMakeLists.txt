cmake_minimum_required (VERSION 3.0)
set (CMAKE_CXX_STANDARD 11)
project (SOBEL)

find_package( OpenCV REQUIRED )
include_directories( ${OpenCV_INCLUDE_DIRS} )

file(GLOB libSource ../lib/*.c ../lib/*.cpp)

add_library(axlib STATIC ${libSource})

add_executable(axsobel axsobel.cpp lib.cpp similarity.cpp )
target_include_directories(axsobel PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../lib)
target_link_libraries( axsobel ${OpenCV_LIBS} axlib )
