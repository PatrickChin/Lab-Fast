cmake_minimum_required(VERSION 3.0)

project(muon)

add_executable(muon muon.c)
target_compile_options(muon PUBLIC -std=c99 -H -Wall)
target_link_libraries(muon PUBLIC m)
