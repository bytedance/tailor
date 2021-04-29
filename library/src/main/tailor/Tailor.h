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

#ifndef TAILOR_H
#define TAILOR_H

#include <stdlib.h>
#include "stream.hpp"
//**************************************************************************************************
#define HPROF_TAG_STRING            0x01
#define HPROF_TAG_LOAD_CLASS        0x02
#define HPROF_TAG_UNLOAD_CLASS      0x03
#define HPROF_TAG_STACK_FRAME       0x04
#define HPROF_TAG_STACK_TRACE       0x05
#define HPROF_TAG_ALLOC_SITES       0x06
#define HPROF_TAG_HEAP_SUMMARY      0x07
#define HPROF_TAG_START_THREAD      0x0A
#define HPROF_TAG_END_THREAD        0x0B
#define HPROF_TAG_HEAP_DUMP         0x0C
#define HPROF_TAG_CPU_SAMPLES       0x0D
#define HPROF_TAG_CONTROL_SETTINGS  0x0E
#define HPROF_TAG_HEAP_DUMP_SEGMENT 0x1C
#define HPROF_TAG_HEAP_DUMP_END     0x2C
//**************************************************************************************************
/* standard */
#define HPROF_ROOT_JNI_GLOBAL       0x01
#define HPROF_ROOT_JNI_LOCAL        0x02
#define HPROF_ROOT_JAVA_FRAME       0x03
#define HPROF_ROOT_NATIVE_STACK     0x04
#define HPROF_ROOT_STICKY_CLASS     0x05
#define HPROF_ROOT_THREAD_BLOCK     0x06
#define HPROF_ROOT_MONITOR_USED     0x07
#define HPROF_ROOT_THREAD_OBJECT    0x08
#define HPROF_CLASS_DUMP            0x20
#define HPROF_INSTANCE_DUMP         0x21
#define HPROF_OBJECT_ARRAY_DUMP     0x22
#define HPROF_PRIMITIVE_ARRAY_DUMP  0x23
#define HPROF_ROOT_UNKNOWN          0xFF
//**************************************************************************************************
/* Android */
#define HPROF_ROOT_INTERNED_STRING        0x89
#define HPROF_ROOT_FINALIZING             0x8A
#define HPROF_ROOT_DEBUGGER               0x8B
#define HPROF_ROOT_REFERENCE_CLEANUP      0x8C
#define HPROF_ROOT_VM_INTERNAL            0x8D
#define HPROF_ROOT_JNI_MONITOR            0x8E
#define HPROF_UNREACHABLE                 0x90
#define HPROF_PRIMITIVE_ARRAY_NODATA_DUMP 0xC3
#define HPROF_HEAP_DUMP_INFO              0xFE
//**************************************************************************************************
/* Hprof basic type */
#define HPROF_BASIC_OBJECT  0x02
#define HPROF_BASIC_BOOLEAN 0x04
#define HPROF_BASIC_CHAR    0x05
#define HPROF_BASIC_FLOAT   0x06
#define HPROF_BASIC_DOUBLE  0x07
#define HPROF_BASIC_BYTE    0x08
#define HPROF_BASIC_SHORT   0x09
#define HPROF_BASIC_INT     0x0A
#define HPROF_BASIC_LONG    0x0B
//**************************************************************************************************
#define INT1(p, s) ((uint8_t)  (p->buffer[p->offset + s]))
#define INT2(p, s) ((uint16_t) (p->buffer[p->offset + s] <<  8) + (p->buffer[p->offset + s + 1]))
#define INT4(p, s) ((uint32_t) (p->buffer[p->offset + s] << 24) + (p->buffer[p->offset + s + 1] << 16) + (p->buffer[p->offset + s + 2] << 8) + p->buffer[p->offset + s + 3])

#define SEEK(p, s) (p->offset += s)

#define FILL(writer, s) fill(writer, s)
#define MOVE(writer, reader, s) fill(writer, reader, s)
#define COPY(writer, reader, s) copy(writer, reader, s)

// 0 is OK, 1 is END, extra is ERROR
int handle(Reader *reader, Writer *writer);
//**************************************************************************************************
//0x01
void handle_STRING(Reader *reader, Writer *writer);

//0x02
void handle_LOAD_CLASS(Reader *reader, Writer *writer);

//0x1C
void handle_HEAP_DUMP_SEGMENT(Reader *reader, Writer *writer);

//0x2c
void handle_HEAP_DUMP_END(Reader *reader, Writer *writer);
//**************************************************************************************************
//0x20
void handle_CLASS_DUMP(Reader *reader, Writer *writer);

//0x21
void handle_INSTANCE_DUMP(Reader *reader, Writer *writer);

//0x22
void handle_OBJECT_ARRAY_DUMP(Reader *reader, Writer *writer);

//0x23
void handle_PRIMITIVE_ARRAY_DUMP(Reader *reader, Writer *writer);
//**************************************************************************************************
#endif //TAILOR_H