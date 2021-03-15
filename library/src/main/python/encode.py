#!/usr/bin/python

#
# Copyright (C) 2020 ByteDance Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import argparse
import os
import zlib

counter = {}


def encode(reader, writer):
    writer.write(bytearray([ord(c) for c in 'JAVA PROFILE 6.0.1']))
    reader.seek(13, 1)

    length = os.path.getsize(reader.name)
    while reader.tell() < length:
        tag = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        if tag == 0x01:  # STRING
            encode_STRING(reader, writer)
        elif tag == 0x02:  # LOAD_CLASS
            encode_LOAD_CLASS(reader, writer)
        elif tag == 0x03:  # UNLOAD_CLASS
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x04:  # STACK_FRAME
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x05:  # STACK_TRACE
            encode_STACK_TRACE(reader, writer)
        elif tag == 0x06:  # ALLOC_SITES
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x07:  # HEAP_SUMMARY
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0A:  # START_THREAD
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0B:  # END_THREAD
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0C:  # HEAP_DUMP
            encode_HEAP_DUMP_SEGMENT(reader, writer)
        elif tag == 0x0D:  # CPU_SAMPLES
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0E:  # CONTROL_SETTINGS
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x1C:  # HEAP_DUMP_SEGMENT
            encode_HEAP_DUMP_SEGMENT(reader, writer)
        elif tag == 0x2C:   # HEAP_DUMP_END
            encode_HEAP_DUMP_END(reader, writer)
        else:
            raise Exception('Not supported tag: %d, length: %d' % (tag, reader.tell()))


def encode_STRING(reader, writer):
    COUNTER('STRING')
    writer.write(bytearray([0x01]))

    reader.seek(6, 1)

    length = int.from_bytes(reader.read(2), byteorder='big', signed=False)
    reader.seek(-2, 1)

    writer.write(bytearray(reader.read(2 + length)))


def encode_LOAD_CLASS(reader, writer):
    COUNTER('LOAD_CLASS')
    writer.write(bytearray([0x02]))
    reader.seek(12, 1)
    writer.write(bytearray(reader.read(4)))
    reader.seek(4, 1)
    writer.write(bytearray(reader.read(4)))


def encode_STACK_TRACE(reader, writer):
    COUNTER('STACK_TRACE')
    reader.seek(16, 1)
    length = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    reader.seek(4 * length, 1)


def encode_HEAP_DUMP_SEGMENT(reader, writer):
    COUNTER('HEAP_DUMP_SEGMENT')
    writer.write(bytearray([0x1C]))
    reader.seek(8, 1)

    while True:
        tag = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        reader.seek(-1, 1)

        if tag == 0x01:    # ROOT_JNI_GLOBAL
            encode_ROOT_JNI_GLOBAL(reader, writer)
        elif tag == 0x02:  # ROOT_JNI_LOCAL
            encode_ROOT_JNI_LOCAL(reader, writer)
        elif tag == 0x03:  # ROOT_JAVA_FRAME
            encode_ROOT_JAVA_FRAME(reader, writer)
        elif tag == 0x04:  # ROOT_NATIVE_STACK
            encode_ROOT_NATIVE_STACK(reader, writer)
        elif tag == 0x05:  # ROOT_STICKY_CLASS
            encode_ROOT_STICKY_CLASS(reader, writer)
        elif tag == 0x06:  # ROOT_THREAD_BLOCK
            encode_ROOT_THREAD_BLOCK(reader, writer)
        elif tag == 0x07:  # ROOT_MONITOR_USED
            encode_ROOT_MONITOR_USED(reader, writer)
        elif tag == 0x08:  # ROOT_THREAD_OBJECT
            encode_ROOT_THREAD_OBJECT(reader, writer)
        elif tag == 0x20:  # CLASS_DUMP
            encode_CLASS_DUMP(reader, writer)
        elif tag == 0x21:  # INSTANCE_DUMP
            encode_INSTANCE_DUMP(reader, writer)
        elif tag == 0x22:  # OBJECT_ARRAY_DUMP
            encode_OBJECT_ARRAY_DUMP(reader, writer)
        elif tag == 0x23:  # PRIMITIVE_ARRAY_DUMP
            encode_PRIMITIVE_ARRAY_DUMP(reader, writer)
        elif tag == 0x89:  # ROOT_INTERNED_STRING
            encode_ROOT_INTERNED_STRING(reader, writer)
        elif tag == 0x8A:  # ROOT_FINALIZING
            encode_ROOT_FINALIZING(reader, writer)
        elif tag == 0x8B:  # ROOT_DEBUGGER
            encode_ROOT_DEBUGGER(reader, writer)
        elif tag == 0x8C:  # ROOT_REFERENCE_CLEANUP
            encode_ROOT_REFERENCE_CLEANUP(reader, writer)
        elif tag == 0x8D:  # ROOT_VM_INTERNAL
            encode_ROOT_VM_INTERNAL(reader, writer)
        elif tag == 0x8E:  # ROOT_JNI_MONITOR
            encode_ROOT_JNI_MONITOR(reader, writer)
        elif tag == 0x90:  # UNREACHABLE
            raise Exception('encode_HEAP_DUMP_SEGMENT >>> Not supported tag: %d' % tag)
        elif tag == 0xC3:  # PRIMITIVE_ARRAY_NODATA_DUMP
            raise Exception('encode_HEAP_DUMP_SEGMENT >>> Not supported tag: %d' % tag)
        elif tag == 0xFE:  # HEAP_DUMP_INFO
            encode_HEAP_DUMP_INFO(reader, writer)
        elif tag == 0xFF:  # ROOT_UNKNOWN
            encode_ROOT_UNKNOWN(reader, writer)
        else:
            break


def encode_HEAP_DUMP_END(reader, writer):
    reader.seek(8, 1)
    writer.write(bytearray([0x2C]))

    global counter
    print(counter)
    print('COMPLETE: %d/%d -> %d' % (reader.tell(), os.path.getsize(reader.name), writer.tell()))


def encode_ROOT_JNI_GLOBAL(reader, writer):
    COUNTER('ROOT_JNI_GLOBAL')
    writer.write(bytearray(reader.read(9)))


def encode_ROOT_JNI_LOCAL(reader, writer):
    COUNTER('ROOT_JNI_LOCAL')
    writer.write(bytearray(reader.read(5)))
    reader.seek(8, 1)


def encode_ROOT_JAVA_FRAME(reader, writer):
    COUNTER('ROOT_JAVA_FRAME')
    writer.write(bytearray(reader.read(5)))
    reader.seek(8, 1)


def encode_ROOT_NATIVE_STACK(reader, writer):
    COUNTER('ROOT_NATIVE_STACK')
    writer.write(bytearray(reader.read(5)))
    reader.seek(4, 1)


def encode_ROOT_STICKY_CLASS(reader, writer):
    COUNTER('ROOT_STICKY_CLASS')
    writer.write(bytearray(reader.read(5)))


def encode_ROOT_THREAD_BLOCK(reader, writer):
    COUNTER('ROOT_THREAD_BLOCK')
    writer.write(bytearray(reader.read(5)))
    reader.seek(4, 1)


def encode_ROOT_MONITOR_USED(reader, writer):
    COUNTER('ROOT_MONITOR_USED')
    writer.write(bytearray(reader.read(5)))


def encode_ROOT_THREAD_OBJECT(reader, writer):
    COUNTER('ROOT_THREAD_OBJECT')
    writer.write(bytearray(reader.read(5)))
    reader.seek(8, 1)


def encode_CLASS_DUMP(reader, writer):
    COUNTER('CLASS_DUMP')
    writer.write(bytearray(reader.read(5)))

    reader.seek(4, 1)

    writer.write(bytearray(reader.read(16)))

    reader.seek(10, 1)

    writer.write(bytearray(reader.read(2)))

    constant_fields_count = int.from_bytes(reader.read(2), byteorder='big', signed=False)
    reader.seek(-2, 1)
    writer.write(bytearray(reader.read(2)))
    encode_CLASS_CONSTANT_FIELDS(reader, constant_fields_count, writer)

    static_fields_count = int.from_bytes(reader.read(2), byteorder='big', signed=False)
    reader.seek(-2, 1)
    writer.write(bytearray(reader.read(2)))
    encode_CLASS_STATIC_FIELDS(reader, static_fields_count, writer)

    instance_fields_count = int.from_bytes(reader.read(2), byteorder='big', signed=False)
    reader.seek(-2, 1)
    writer.write(bytearray(reader.read(2)))
    encode_CLASS_INSTANCE_FIELDS(reader, instance_fields_count,  writer)


def encode_INSTANCE_DUMP(reader, writer):
    COUNTER('INSTANCE_DUMP')
    writer.write(bytearray(reader.read(5)))
    reader.seek(4, 1)
    writer.write(bytearray(reader.read(4)))

    bytes_followed = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    reader.seek(-4, 1)
    writer.write(bytearray(reader.read(4 + bytes_followed)))


def encode_OBJECT_ARRAY_DUMP(reader, writer):
    COUNTER('OBJECT_ARRAY_DUMP')
    writer.write(bytearray(reader.read(5)))

    reader.seek(4, 1)

    length = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    reader.seek(-4, 1)

    writer.write(bytearray(reader.read(8 + 4 * length)))


def encode_PRIMITIVE_ARRAY_DUMP(reader, writer):
    COUNTER('PRIMITIVE_ARRAY_DUMP')
    writer.write(bytearray(reader.read(5)))

    reader.seek(4, 1)

    length = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    type = int.from_bytes(reader.read(1), byteorder='big', signed=False)

    reader.seek(-5, 1)
    writer.write(bytearray(reader.read(5)))

    encode_PRIMITIVE_ARRAY_ELEMENTS(reader, length, type, writer)


def encode_ROOT_INTERNED_STRING(reader, writer):
    COUNTER('ROOT_INTERNED_STRING')
    writer.write(bytearray(reader.read(5)))


def encode_ROOT_FINALIZING(reader, writer):
    COUNTER('ROOT_FINALIZING')
    writer.write(bytearray(reader.read(5)))


def encode_ROOT_DEBUGGER(reader, writer):
    COUNTER('ROOT_DEBUGGER')
    writer.write(bytearray(reader.read(5)))


def encode_ROOT_REFERENCE_CLEANUP(reader, writer):
    COUNTER('ROOT_REFERENCE_CLEANUP')
    writer.write(bytearray(reader.read(5)))


def encode_ROOT_VM_INTERNAL(reader, writer):
    COUNTER('ROOT_VM_INTERNAL')
    writer.write(bytearray(reader.read(5)))


def encode_ROOT_JNI_MONITOR(reader, writer):
    COUNTER('ROOT_JNI_MONITOR')
    writer.write(bytearray(reader.read(5)))
    reader.seek(8, 1)


def encode_HEAP_DUMP_INFO(reader, writer):
    COUNTER('HEAP_DUMP_INFO')
    writer.write(bytearray(reader.read(9)))


def encode_ROOT_UNKNOWN(reader, writer):
    COUNTER('ROOT_UNKNOWN')
    writer.write(bytearray(reader.read(5)))


def encode_PRIMITIVE_ARRAY_ELEMENTS(reader, length, type, writer):
    if type >= 12 or type == 3 or type <= 1:
        raise Exception('encode_PRIMITIVE_ARRAY_ELEMENTS() Not supported type: %d' % type)
    elif type == 2:   # object
        writer.write(bytearray(reader.read(4 * length)))
    elif type == 4:   # boolean
        writer.write(bytearray(reader.read(1 * length)))
    elif type == 5:   # char
        reader.seek(2 * length, 1)
    elif type == 6:   # float
        writer.write(bytearray(reader.read(4 * length)))
    elif type == 7:   # double
        writer.write(bytearray(reader.read(8 * length)))
    elif type == 8:   # byte
        reader.seek(1 * length, 1)
    elif type == 9:   # short
        writer.write(bytearray(reader.read(2 * length)))
    elif type == 10:  # int
        writer.write(bytearray(reader.read(4 * length)))
    elif type == 11:  # long
        writer.write(bytearray(reader.read(8 * length)))
    else:
        raise Exception('encode_PRIMITIVE_ARRAY_ELEMENTS() not supported type ' % type)


def encode_CLASS_CONSTANT_FIELDS(reader, count, writer):
    while count > 0:
        count -= 1

        reader.seek(2, 1)
        type = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        reader.seek(-3, 1)

        if type >= 12 or type == 3 or type <= 1:
            raise Exception('encode_CLASS_CONSTANT_FIELDS() not supported type ' % type)
        elif type == 2:   # object
            writer.write(bytearray(reader.read(3 + 4)))
        elif type == 4:   # boolean
            writer.write(bytearray(reader.read(3 + 1)))
        elif type == 5:   # char
            writer.write(bytearray(reader.read(3 + 2)))
        elif type == 6:   # float
            writer.write(bytearray(reader.read(3 + 4)))
        elif type == 7:   # double
            writer.write(bytearray(reader.read(3 + 8)))
        elif type == 8:   # byte
            writer.write(bytearray(reader.read(3 + 1)))
        elif type == 9:   # short
            writer.write(bytearray(reader.read(3 + 2)))
        elif type == 10:  # int
            writer.write(bytearray(reader.read(3 + 4)))
        elif type == 11:  # long
            writer.write(bytearray(reader.read(3 + 8)))
        else:
            raise Exception('encode_CLASS_CONSTANT_FIELDS() not supported type ' % type)


def encode_CLASS_STATIC_FIELDS(reader, count, writer):
    while count > 0:
        count -= 1

        reader.seek(4, 1)
        type = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        reader.seek(-5, 1)

        if type >= 12 or type == 3 or type <= 1:
            raise Exception('encode_CLASS_STATIC_FIELDS() not supported type ' % type)
        elif type == 2:   # object
            writer.write(bytearray(reader.read(5 + 4)))
        elif type == 4:   # boolean
            writer.write(bytearray(reader.read(5 + 1)))
        elif type == 5:   # char
            writer.write(bytearray(reader.read(5 + 2)))
        elif type == 6:   # float
            writer.write(bytearray(reader.read(5 + 4)))
        elif type == 7:   # double
            writer.write(bytearray(reader.read(5 + 8)))
        elif type == 8:   # byte
            writer.write(bytearray(reader.read(5 + 1)))
        elif type == 9:   # short
            writer.write(bytearray(reader.read(5 + 2)))
        elif type == 10:  # int
            writer.write(bytearray(reader.read(5 + 4)))
        elif type == 11:  # long
            writer.write(bytearray(reader.read(5 + 8)))
        else:
            raise Exception('encode_CLASS_STATIC_FIELDS() not supported type ' % type)


def encode_CLASS_INSTANCE_FIELDS(reader, count, writer):
    while count > 0:
        count -= 1

        reader.seek(4, 1)
        type = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        reader.seek(-5, 1)

        if type >= 12 or type == 3 or type <= 1:
            raise Exception('encode_CLASS_INSTANCE_FIELDS() not supported type ' % type)
        else:
            writer.write(bytearray(reader.read(5)))


def COUNTER(key):
    global counter
    counter.update({key: 1 + counter.get(key, 0)})


def compress(reader, writer):
    instance = zlib.compressobj(6)
    buffer = reader.read(1024 * 1024)
    while buffer:
        try:
            writer.write(instance.compress(buffer))
        except:
            raise Exception('compress failed')
        buffer = reader.read(1024 * 1024)
    writer.write(instance.flush())


def process(source, target):
    reader =  None

    try:
        reader = open(source, 'rb')
        writer = open('.tailor', 'wb')
        if reader.read(18).decode('ascii') == 'JAVA PROFILE 1.0.3':
            encode(reader, writer)
        else:
            raise Exception('encode failed: unknown file format !')
        reader.close()
        writer.close()
    except Exception as e:
        print(e)
        print('decompress failed at: %d/%d' % (reader.tell(), os.path.getsize(reader.name)))

    try:
        reader = open('.tailor', 'rb')
        writer = open(target, 'wb')
        compress(reader, writer)
        reader.close()
        writer.close()
    except Exception as e:
        print(e)
        print('decompress failed at: %d/%d' % (reader.tell(), os.path.getsize(reader.name)))


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--input', help='input file name')
    argParser.add_argument('-o', '--output', help='output file name')
    args = argParser.parse_args()

    if not args.input:
        raise Exception('ERROR: input file name should not be null, using -h or --help for detail')
    if not args.output:
        raise Exception('ERROR: output file name should not be null, using -h or --help for detail')

    process(args.input, args.output)

