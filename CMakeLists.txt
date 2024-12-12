cmake_minimum_required(VERSION 3.20)
project(project-2)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_VERBOSE_MAKEFILE ON)

link_libraries( ws2_32 ) 

add_compile_options (   -Wall 
                        -Wextra
                        -pedantic
                        -g          )

add_executable  (   server  
                    Server.cpp
                    HTTP_Handler.cpp     )

set(CMAKE_VERBOSE_MAKEFILE OFF)