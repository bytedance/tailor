/*
 * Copyright (C) 2020 ByteDance Inc
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <string.h>
#include <jni.h>
#include <fcntl.h>
#include <unistd.h>

#include "xh_core.h"

#include "logger.h"
#include "Tailor.h"

#include "ByteReader.hpp"
#include "FileReader.hpp"
#include "FileWriter.hpp"
#include "LibzWriter.hpp"
//**************************************************************************************************
const char *VERSION = "JAVA PROFILE 6.0.1";
//**************************************************************************************************
Reader *reader = nullptr;
Writer *writer = nullptr;
volatile int target = -1;

inline Writer* createWriter(const char *name, bool gzip) {
    if (gzip) {
        return new LibzWriter(name);
    } else {
        return new FileWriter(name);
    }
}

inline ssize_t handle(const char *buffer, size_t count) {
    reader->buffer = const_cast<char *>(buffer);
    reader->length = count;
    reader->offset = 0;

    int result = 0;
    while (reader->isAvailable() && (result = handle(reader, writer)) == 0);
    if (result == 1) {
        target = -1;
    }

    return count;
}

int open_proxy(const char *path, int flags, mode_t mode) {
    if (writer != nullptr && strcmp(writer->name, path) == 0) {
        return target = writer->proxy(flags, mode);
    } else {
        return open(path, flags, mode);
    }
}

ssize_t write_proxy(int fd, const char *buffer, size_t count) {
    if (target == fd) {
        return handle(buffer, count);
    } else {
        return write(fd, buffer, count);
    }
}

int hook() {
    int state = 0;
    state |= xh_core_register(".*\\.so$", "open", (void *) open_proxy, nullptr);
    state |= xh_core_register(".*\\.so$", "write", (void *) write_proxy, nullptr);
    state |= xh_core_ignore(".*libtailor\\.so$", "open");
    state |= xh_core_ignore(".*libtailor\\.so$", "write");
    state |= xh_core_refresh(0);
    return state;
}

void Tailor_nOpenProxy(JNIEnv* env, jobject obj, jstring name, jboolean gzip) {
    target = -1;
    reader = new ByteReader();
    writer = createWriter(env->GetStringUTFChars(name, 0), gzip);
    fill(writer, const_cast<char *>(VERSION), 18);
    LOGGER(">>> open %s", ((0 == hook()) ? "success" : "failure"));
}

void Tailor_nCloseProxy(JNIEnv *env, jobject obj) {
    delete reader;
    reader = nullptr;

    delete writer;
    writer = nullptr;

    xh_core_clear();
}

void Tailor_nCropHprof(JNIEnv *env, jobject obj, jstring source, jstring target, bool gzip) {
    Writer *writer = createWriter(env->GetStringUTFChars(target, 0), gzip);
    fill(writer, const_cast<char *>(VERSION), 18);

    Reader *reader = new FileReader(env->GetStringUTFChars(source, 0));
    while (reader->isAvailable() && handle(reader, writer) == 0);

    delete writer;
}

static const JNINativeMethod sMethods[] = {
        {
                "nOpenProxy",
                "(Ljava/lang/String;Z)V",
                (void *) Tailor_nOpenProxy
        }, {
                "nCloseProxy",
                "()V",
                (void *) Tailor_nCloseProxy
        }, {
                "nCropHprof",
                "(Ljava/lang/String;Ljava/lang/String;Z)V",
                (void *) Tailor_nCropHprof
        }
};

static int registerNativeImpl(JNIEnv *env) {
    jclass clazz = env->FindClass("com/bytedance/tailor/Tailor");
    if (clazz == nullptr) {
        return JNI_FALSE;
    }

    if (env->RegisterNatives(clazz, sMethods, sizeof(sMethods) / sizeof(sMethods[0])) < 0) {
        return JNI_FALSE;
    } else {
        return JNI_TRUE;
    }
}

JNIEXPORT jint JNI_OnLoad(JavaVM *vm, void *res) {
    JNIEnv *env = nullptr;
    if (vm->GetEnv((void **) &env, JNI_VERSION_1_6) != JNI_OK) {
        return -1;
    }

    if (env == nullptr || registerNativeImpl(env) == 0) {
        return -1;
    } else {
        return JNI_VERSION_1_6;
    }
}