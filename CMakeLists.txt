cmake_minimum_required(VERSION 3.0)

project(muon)

add_executable(tobin muon.c tobin.c)
target_compile_options(tobin PUBLIC -std=c99 -Wall)
target_link_libraries(tobin PUBLIC m)

add_executable(readbin muon.c readbin.c)
target_compile_options(readbin PUBLIC -std=c99 -Wall)
target_link_libraries(readbin PUBLIC m)
