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

#ifndef FILE_READER_H
#define FILE_READER_H

#include "stream.hpp"
#include <sys/mman.h>
//**************************************************************************************************
class FileReader : public Reader {
public:
    FileReader(const char *name);
    ~FileReader();
public:
    bool isAvailable();
private:
    FILE *source;
};
//**************************************************************************************************
FileReader::FileReader(const char *name) {
    source = fopen(name, "r");

    fseek(source, 0, SEEK_END);
    length = ftell(source);

    buffer = (char *) mmap(NULL, length, PROT_READ, MAP_SHARED, fileno(source), 0);
    offset = 0;
}

FileReader::~FileReader() {
    fclose(source);
    source = nullptr;

    munmap(buffer, length);
    buffer = nullptr;

    length = 0;
    offset = 0;
}

bool FileReader::isAvailable() {
    return buffer != nullptr && length > offset;
}
#endif //FILE_READER_H