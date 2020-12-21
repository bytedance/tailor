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

#include "logger.h"
#include "Tailor.h"
//**************************************************************************************************
int handle(Reader *reader, Writer *writer) {
    uint8_t tag = INT1(reader, 0);
    switch (tag) {
    case 0x4A:
        SEEK(reader, 31);            //"JAVA PROFILE 1.0.X";
        return 0;
    case HPROF_TAG_STRING:           // 0x01
        handle_STRING(reader, writer);
        return 0;
    case HPROF_TAG_LOAD_CLASS:       // 0x02
        handle_LOAD_CLASS(reader, writer);
        return 0;
    case HPROF_TAG_HEAP_DUMP:        // 0x0C
    case HPROF_TAG_HEAP_DUMP_SEGMENT:// 0x1C
        handle_HEAP_DUMP_SEGMENT(reader, writer);
        return 0;
    case HPROF_TAG_HEAP_DUMP_END:    // 0x2C
        handle_HEAP_DUMP_END(reader, writer);
        return 1;
    default:                         // unsupported tag
        SEEK(reader, 9 + INT4(reader, 5));
        return 0;
    }
}

//0x01
void handle_STRING(Reader *reader, Writer *writer) {
    FILL(writer, 0x01);
    SEEK(reader, 7);
    COPY(writer, reader, 2 + INT2(reader, 0));
}

//0x02
void handle_LOAD_CLASS(Reader *reader, Writer *writer) {
    FILL(writer, 0x02);
    SEEK(reader, 13);
    MOVE(writer, reader, 4);
    SEEK(reader, 4);
    MOVE(writer, reader, 4);
}

//0x2C
void handle_HEAP_DUMP_SEGMENT(Reader *reader, Writer *writer) {
    FILL(writer, 0x1C);
    SEEK(reader, 9);

    while (reader->isAvailable()) {
        uint8_t tag = INT1(reader, 0);
        switch (tag) {
        case HPROF_ROOT_JNI_GLOBAL:            // 0x01
        case HPROF_HEAP_DUMP_INFO:             // 0xFE
            MOVE(writer, reader, 9);
            break;
        case HPROF_ROOT_JNI_LOCAL:             // 0x02
        case HPROF_ROOT_JAVA_FRAME:            // 0x03
        case HPROF_ROOT_THREAD_OBJECT:         // 0x08
        case HPROF_ROOT_JNI_MONITOR:           // 0x8E
            MOVE(writer, reader, 5);
            SEEK(reader, 8);
            break;
        case HPROF_ROOT_NATIVE_STACK:          // 0x04
        case HPROF_ROOT_THREAD_BLOCK:          // 0x06
            MOVE(writer, reader, 5);
            SEEK(reader, 4);
            break;
        case HPROF_ROOT_STICKY_CLASS:          // 0x05
        case HPROF_ROOT_MONITOR_USED:          // 0x07
        case HPROF_ROOT_INTERNED_STRING:       // 0x89
        case HPROF_ROOT_FINALIZING:            // 0x8A
        case HPROF_ROOT_DEBUGGER:              // 0x8B
        case HPROF_ROOT_REFERENCE_CLEANUP:     // 0x8C
        case HPROF_ROOT_VM_INTERNAL:           // 0x8D
        case HPROF_ROOT_UNKNOWN:               // 0xFF
            MOVE(writer, reader, 5);
            break;
        case HPROF_CLASS_DUMP:                 // 0x20
            handle_CLASS_DUMP(reader, writer);
            break;
        case HPROF_INSTANCE_DUMP:              // 0x21
            handle_INSTANCE_DUMP(reader, writer);
            break;
        case HPROF_OBJECT_ARRAY_DUMP:          // 0x22
            handle_OBJECT_ARRAY_DUMP(reader, writer);
            break;
        case HPROF_PRIMITIVE_ARRAY_DUMP:       // 0x23
            handle_PRIMITIVE_ARRAY_DUMP(reader, writer);
            break;
        default:
            return;
        }
    }
}

//0x2C
void handle_HEAP_DUMP_END(Reader *reader, Writer *writer) {
    FILL(writer, 0x2C);
    SEEK(reader, 9);
}

inline int bytes(int type) {
    switch (type) {
        case HPROF_BASIC_BOOLEAN:
        case HPROF_BASIC_BYTE:
            return 1;
        case HPROF_BASIC_CHAR:
        case HPROF_BASIC_SHORT:
            return 2;
        case HPROF_BASIC_FLOAT:
        case HPROF_BASIC_OBJECT:
        case HPROF_BASIC_INT:
            return 4;
        case HPROF_BASIC_DOUBLE:
        case HPROF_BASIC_LONG:
            return 8;
        default:
            return 0;
    }
}

//0x20
void handle_CLASS_DUMP(Reader *reader, Writer *writer) {
    MOVE(writer, reader, 5);
    SEEK(reader, 4);
    MOVE(writer, reader, 16);
    SEEK(reader, 10);

    uint32_t offset = 2;

    uint16_t constant_fields_count = INT2(reader, offset);
    offset += 2;
    while (constant_fields_count-- > 0) {
        offset += 3 + bytes(INT1(reader, offset + 2));
    }

    uint16_t static_fields_count = INT2(reader, offset);
    offset += 2;
    while (static_fields_count-- > 0) {
        offset += 5 + bytes(INT1(reader, offset + 4));
    }

    uint16_t instance_fields_count = INT2(reader, offset);
    offset += 2 + 5 * instance_fields_count;

    COPY(writer, reader, offset);
}

//0x21
void handle_INSTANCE_DUMP(Reader *reader, Writer *writer) {
    MOVE(writer, reader, 5);
    SEEK(reader, 4);
    COPY(writer, reader, 8 + INT4(reader, 4));
}

//0x22
void handle_OBJECT_ARRAY_DUMP(Reader *reader, Writer *writer) {
    MOVE(writer, reader, 5);
    SEEK(reader, 4);
    COPY(writer, reader, 8 + INT4(reader, 0) * 4);
}

//0x23
void handle_PRIMITIVE_ARRAY_DUMP(Reader *reader, Writer *writer) {
    MOVE(writer, reader, 5);
    SEEK(reader, 4);

    uint32_t count = INT4(reader, 0);
    uint8_t type = INT1(reader, 4);
    if (type == HPROF_BASIC_CHAR || type == HPROF_BASIC_BYTE) {
        MOVE(writer, reader, 5);
        SEEK(reader, count * bytes(type));
    } else {
        COPY(writer, reader, 5 + count * bytes(type));
    }
}