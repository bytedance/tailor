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

#ifndef FILE_WRITER_H
#define FILE_WRITER_H

#include <unistd.h>
#include "stream.hpp"
//**************************************************************************************************
class FileWriter : public Writer {
public:
    FileWriter(const char *name);
    ~FileWriter();
public:
     int proxy(int flags, mode_t mode);
    void flush(char *buff, size_t bytes, bool isEof);
};
//**************************************************************************************************
FileWriter::FileWriter(const char *path) {
    name = path;
    wrap = -1;

    target = fopen(path, "w");
    offset = 0;
}

FileWriter::~FileWriter() {
    fwrite(buffer, 1, offset, target);
    offset = 0;

    fflush(target);
    fclose(target);
    target = nullptr;

    if (wrap != -1) close(wrap);
}

int FileWriter::proxy(int flags, mode_t mode) {
    char proxy[FILE_PATH_LIMIT];
    if (snprintf(proxy, FILE_PATH_LIMIT, "%s.proxy", name) >= FILE_PATH_LIMIT) {
        return wrap = -1;
    } else {
        return wrap = open(proxy, flags, mode);
    }
}

void FileWriter::flush(char *buff, size_t bytes, bool isEof) {
    fwrite(buff, 1, bytes, target);
}
#endif //FILE_WRITER_H