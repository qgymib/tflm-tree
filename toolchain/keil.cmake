# Keil toolchain
#
# [REQUIREMENTS]
# The armclang compiler must be installed on the system and in the path.

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR cortex-m4)

set(CMAKE_C_COMPILER armclang.exe)
set(CMAKE_CXX_COMPILER ${CMAKE_C_COMPILER})
