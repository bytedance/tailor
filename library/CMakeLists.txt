# For more information about using CMake with Android Studio, read the
# documentation: https://d.android.com/studio/projects/add-native-code.html

# Sets the minimum version of CMake required to build the native library.

cmake_minimum_required(VERSION 3.4.1)

# Creates and names a library, sets it as either STATIC
# or SHARED, and provides the relative paths to its source code.
# You can define multiple libraries, and CMake builds them for you.
# Gradle automatically packages shared libraries with your APK.

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Werror=return-type ")
#set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fsanitize=address -fno-omit-frame-pointer")
#set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address -fno-omit-frame-pointer")
#set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -fsanitize=address")
#set(CMAKE_STATIC_LINKER_FLAGS "${CMAKE_STATIC_LINKER_FLAGS} -fsanitize=address")

# Header file directories
include_directories(
        ${CMAKE_SOURCE_DIR}/src/main/xHook
)

add_library(
        # Sets the name of the library.
        tailor

        # Sets the library as a shared library.
        SHARED

        # Provides a relative path to your source file(s).

        src/main/xHook/xh_core.c
        src/main/xHook/xh_core.h
        src/main/xHook/xh_elf.c
        src/main/xHook/xh_elf.h
        src/main/xHook/xh_util.c
        src/main/xHook/xh_util.h
        src/main/xHook/xh_errno.h
        src/main/xHook/queue.h
        src/main/xHook/tree.h
        src/main/xHook/xh_log.h
        src/main/xHook/xh_log.c

        src/main/tailor/ByteReader.hpp
        src/main/tailor/FileReader.hpp
        src/main/tailor/FileWriter.hpp
        src/main/tailor/LibzWriter.hpp
        src/main/tailor/Tailor.cpp
        src/main/tailor/xloader.cpp
)

# Searches for a specified prebuilt library and stores the path as a
# variable. Because CMake includes system libraries in the search path by
# default, you only need to specify the name of the public NDK library
# you want to add. CMake verifies that the library exists before
# completing its build.

find_library(
        # Sets the name of the path variable.
        log-lib

        # Specifies the name of the NDK library that
        # you want CMake to locate.
        log
)

# Specifies libraries CMake should link to your target library. You
# can link multiple libraries, such as libraries you define in this
# build script, prebuilt third-party libraries, or system libraries.

target_link_libraries(
        # Specifies the target library.
        tailor

        # Links the target library to the log library
        # included in the NDK.
        ${log-lib}
        -lz
)