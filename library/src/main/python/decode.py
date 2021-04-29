# coding=utf-8
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


def decode(reader, writer):
    writer.write(bytearray([ord(c) for c in 'JAVA PROFILE 1.0.3']))
    writer.write(bytearray([0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    length = os.path.getsize(reader.name)
    while reader.tell() < length:
        tag = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        if tag == 0x01:    # STRING
            decode_STRING(reader, writer)
        elif tag == 0x02:  # LOAD_CLASS
            decode_LOAD_CLASS(reader, writer)
        elif tag == 0x03:  # UNLOAD_CLASS
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x04:  # STACK_FRAME
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x05:  # STACK_TRACE
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x06:  # ALLOC_SITES
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x07:  # HEAP_SUMMARY
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0A:  # START_THREAD
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0B:  # END_THREAD
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0C:  # HEAP_DUMP
            decode_HEAP_DUMP_SEGMENT(reader, writer)
        elif tag == 0x0D:  # CPU_SAMPLES
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0E:  # CONTROL_SETTINGS
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x1C:  # HEAP_DUMP_SEGMENT
            decode_HEAP_DUMP_SEGMENT(reader, writer)
        elif tag == 0x2C:  # HEAP_DUMP_END
            decode_HEAP_DUMP_END(reader, writer)
        else:
            raise Exception('Not supported tag: %d, length: %d' % (tag, reader.tell()))


def decode_STRING(reader, writer):
    COUNTER('STRING')
    writer.write(bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    length = int.from_bytes(reader.read(2), byteorder='big', signed=False)
    reader.seek(-2, 1)

    writer.write(bytearray(reader.read(2 + length)))


def decode_LOAD_CLASS(reader, writer):
    COUNTER('LOAD_CLASS')
    writer.write(bytearray([0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00]))
    writer.write(bytearray(reader.read(4)))
    writer.write(bytearray(4))
    writer.write(bytearray(reader.read(4)))


def decode_HEAP_DUMP_SEGMENT(reader, writer):
    COUNTER('HEAP_DUMP_SEGMENT')
    writer.write(bytearray([0x1C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    segment_started_index = writer.tell()
    while True:
        tag = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        reader.seek(-1, 1)

        if tag == 0x01:    # ROOT_JNI_GLOBAL
            decode_ROOT_JNI_GLOBAL(reader, writer)
        elif tag == 0x02:  # ROOT_JNI_LOCAL
            decode_ROOT_JNI_LOCAL(reader, writer)
        elif tag == 0x03:  # ROOT_JAVA_FRAME
            decode_ROOT_JAVA_FRAME(reader, writer)
        elif tag == 0x04:  # ROOT_NATIVE_STACK
            decode_ROOT_NATIVE_STACK(reader, writer)
        elif tag == 0x05:  # ROOT_STICKY_CLASS
            decode_ROOT_STICKY_CLASS(reader, writer)
        elif tag == 0x06:  # ROOT_THREAD_BLOCK
            decode_ROOT_THREAD_BLOCK(reader, writer)
        elif tag == 0x07:  # ROOT_MONITOR_USED
            decode_ROOT_MONITOR_USED(reader, writer)
        elif tag == 0x08:  # ROOT_THREAD_OBJECT
            decode_ROOT_THREAD_OBJECT(reader, writer)
        elif tag == 0x20:  # CLASS_DUMP
            decode_CLASS_DUMP(reader, writer)
        elif tag == 0x21:  # INSTANCE_DUMP
            decode_INSTANCE_DUMP(reader, writer)
        elif tag == 0x22:  # OBJECT_ARRAY_DUMP
            decode_OBJECT_ARRAY_DUMP(reader, writer)
        elif tag == 0x23:  # PRIMITIVE_ARRAY_DUMP
            decode_PRIMITIVE_ARRAY_DUMP(reader, writer)
        elif tag == 0x89:  # ROOT_INTERNED_STRING
            decode_ROOT_INTERNED_STRING(reader, writer)
        elif tag == 0x8A:  # ROOT_FINALIZING
            decode_ROOT_FINALIZING(reader, writer)
        elif tag == 0x8B:  # ROOT_DEBUGGER
            decode_ROOT_DEBUGGER(reader, writer)
        elif tag == 0x8C:  # ROOT_REFERENCE_CLEANUP
            verify_ROOT_REFERENCE_CLEANUP(reader, writer)
        elif tag == 0x8D:  # ROOT_VM_INTERNAL
            decode_ROOT_VM_INTERNAL(reader, writer)
        elif tag == 0x8E:  # ROOT_JNI_MONITOR
            decode_ROOT_JNI_MONITOR(reader, writer)
        elif tag == 0x90:  # UNREACHABLE
            raise Exception('decode_HEAP_DUMP_SEGMENT >>> Not supported tag: %d' % tag)
        elif tag == 0xC3:  # PRIMITIVE_ARRAY_NODATA_DUMP
            raise Exception('decode_HEAP_DUMP_SEGMENT >>> Not supported tag: %d' % tag)
        elif tag == 0xFE:  # HEAP_DUMP_INFO
            decode_HEAP_DUMP_INFO(reader, writer)
        elif tag == 0xFF:  # ROOT_UNKNOWN
            decode_ROOT_UNKNOWN(reader, writer)
        else:
            break

    segment_stopped_index = writer.tell()
    if segment_started_index == segment_stopped_index:
        writer.seek(-9, 1)
    else:
        length = segment_stopped_index - segment_started_index
        writer.seek(-4 - length, 1)
        writer.write(bytearray([(length & 0XFF000000) >> 24, (length & 0X00FF0000) >> 16, (length & 0X0000FF00) >> 8, length & 0X000000FF]))
        writer.seek(segment_stopped_index, 0)


def decode_HEAP_DUMP_END(reader, writer):
    writer.write(bytearray([0x2C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

    global counter
    print(counter)
    print('success: [%d/%d -> %d]' % (reader.tell(), os.path.getsize(reader.name), writer.tell()))


def decode_ROOT_JNI_GLOBAL(reader, writer):
    COUNTER('ROOT_JNI_GLOBAL')
    writer.write(bytearray(reader.read(9)))


def decode_ROOT_JNI_LOCAL(reader, writer):
    COUNTER('ROOT_JNI_LOCAL')
    writer.write(bytearray(reader.read(5)))
    writer.write(bytearray(8))


def decode_ROOT_JAVA_FRAME(reader, writer):
    COUNTER('ROOT_JAVA_FRAME')
    writer.write(bytearray(reader.read(5)))
    writer.write(bytearray(8))


def decode_ROOT_NATIVE_STACK(reader, writer):
    COUNTER('ROOT_NATIVE_STACK')
    writer.write(bytearray(reader.read(5)))
    writer.write(bytearray(4))


def decode_ROOT_STICKY_CLASS(reader, writer):
    COUNTER('ROOT_STICKY_CLASS')
    writer.write(bytearray(reader.read(5)))


def decode_ROOT_THREAD_BLOCK(reader, writer):
    COUNTER('ROOT_THREAD_BLOCK')
    writer.write(bytearray(reader.read(5)))
    writer.write(bytearray(4))


def decode_ROOT_MONITOR_USED(reader, writer):
    COUNTER('ROOT_MONITOR_USED')
    writer.write(bytearray(reader.read(5)))


def decode_ROOT_THREAD_OBJECT(reader, writer):
    COUNTER('ROOT_THREAD_OBJECT')
    writer.write(bytearray(reader.read(5)))
    writer.write(bytearray(8))


def decode_CLASS_DUMP(reader, writer):
    COUNTER('CLASS_DUMP')
    writer.write(bytearray(reader.read(5)))

    writer.write(bytearray(4))

    writer.write(bytearray(reader.read(16)))

    writer.write(bytearray(10))

    writer.write(bytearray(reader.read(2)))

    constant_fields_count = int.from_bytes(reader.read(2), byteorder='big', signed=False)
    reader.seek(-2, 1)
    writer.write(bytearray(reader.read(2)))
    decode_CLASS_CONSTANT_FIELDS(reader, constant_fields_count, writer)

    static_fields_count = int.from_bytes(reader.read(2), byteorder='big', signed=False)
    reader.seek(-2, 1)
    writer.write(bytearray(reader.read(2)))
    decode_CLASS_STATIC_FIELDS(reader, static_fields_count, writer)

    instance_fields_count = int.from_bytes(reader.read(2), byteorder='big', signed=False)
    reader.seek(-2, 1)
    writer.write(bytearray(reader.read(2)))
    decode_CLASS_INSTANCE_FIELDS(reader, instance_fields_count, writer)


def decode_INSTANCE_DUMP(reader, writer):
    COUNTER('INSTANCE_DUMP')
    writer.write(bytearray(reader.read(5)))
    writer.write(bytearray(4))
    writer.write(bytearray(reader.read(4)))

    bytes_followed = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    reader.seek(-4, 1)
    writer.write(bytearray(reader.read(4 + bytes_followed)))


def decode_OBJECT_ARRAY_DUMP(reader, writer):
    COUNTER('OBJECT_ARRAY_DUMP')
    writer.write(bytearray(reader.read(5)))

    writer.write(bytearray(4))

    length = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    reader.seek(-4, 1)

    writer.write(bytearray(reader.read(8 + 4 * length)))


def decode_PRIMITIVE_ARRAY_DUMP(reader, writer):
    COUNTER('PRIMITIVE_ARRAY_DUMP')
    writer.write(bytearray(reader.read(5)))

    writer.write(bytearray(4))

    length = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    type = int.from_bytes(reader.read(1), byteorder='big', signed=False)

    reader.seek(-5, 1)
    writer.write(bytearray(reader.read(5)))

    decode_PRIMITIVE_ARRAY_ELEMENTS(reader, length, type, writer)


def decode_ROOT_INTERNED_STRING(reader, writer):
    COUNTER('ROOT_INTERNED_STRING')
    writer.write(bytearray(reader.read(5)))


def decode_ROOT_FINALIZING(reader, writer):
    COUNTER('ROOT_FINALIZING')
    writer.write(bytearray(reader.read(5)))


def decode_ROOT_DEBUGGER(reader, writer):
    COUNTER('ROOT_DEBUGGER')
    writer.write(bytearray(reader.read(5)))


def verify_ROOT_REFERENCE_CLEANUP(reader, writer):
    COUNTER('ROOT_REFERENCE_CLEANUP')
    writer.write(bytearray(reader.read(5)))


def decode_ROOT_VM_INTERNAL(reader, writer):
    COUNTER('ROOT_VM_INTERNAL')
    writer.write(bytearray(reader.read(5)))


def decode_ROOT_JNI_MONITOR(reader, writer):
    COUNTER('ROOT_JNI_MONITOR')
    writer.write(bytearray(reader.read(5)))
    writer.write(bytearray(8))


def decode_HEAP_DUMP_INFO(reader, writer):
    COUNTER('HEAP_DUMP_INFO')
    writer.write(bytearray(reader.read(9)))


def decode_ROOT_UNKNOWN(reader, writer):
    COUNTER('ROOT_UNKNOWN')
    writer.write(bytearray(reader.read(5)))


def decode_PRIMITIVE_ARRAY_ELEMENTS(reader, length, type, writer):
    if type >= 12 or type == 3 or type <= 1:
        raise Exception('decode_PRIMITIVE_ARRAY_ELEMENTS() not supported type ' % type)
    elif type == 2:   # object
        writer.write(bytearray(reader.read(4 * length)))
    elif type == 4:   # boolean
        writer.write(bytearray(reader.read(1 * length)))
    elif type == 5:   # char
        writer.write(bytearray(2 * length))
    elif type == 6:   # float
        writer.write(bytearray(reader.read(4 * length)))
    elif type == 7:   # double
        writer.write(bytearray(reader.read(8 * length)))
    elif type == 8:   # byte
        writer.write(bytearray(1 * length))
    elif type == 9:   # short
        writer.write(bytearray(reader.read(2 * length)))
    elif type == 10:  # int
        writer.write(bytearray(reader.read(4 * length)))
    elif type == 11:  # long
        writer.write(bytearray(reader.read(8 * length)))
    else:
        raise Exception('decode_PRIMITIVE_ARRAY_ELEMENTS() not supported type ' % type)


def decode_CLASS_CONSTANT_FIELDS(reader, count, writer):
    while count > 0:
        count -= 1

        reader.seek(2, 1)
        type = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        reader.seek(-3, 1)

        if type >= 12 or type == 3 or type <= 1:
            raise Exception('decode_CLASS_CONSTANT_FIELDS() not supported type ' % type)
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
            raise Exception('decode_CLASS_CONSTANT_FIELDS() not supported type ' % type)


def decode_CLASS_STATIC_FIELDS(reader, count, writer):
    while count > 0:
        count -= 1

        reader.seek(4, 1)
        type = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        reader.seek(-5, 1)

        if type >= 12 or type == 3 or type <= 1:
            raise Exception('decode_CLASS_STATIC_FIELDS() not supported type ' % type)
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
            raise Exception('decode_CLASS_STATIC_FIELDS() not supported type ' % type)


def decode_CLASS_INSTANCE_FIELDS(reader, count, writer):
    while count > 0:
        count -= 1

        reader.seek(4, 1)
        type = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        reader.seek(-5, 1)

        if type >= 12 or type == 3 or type <= 1:
            raise Exception('decode_CLASS_INSTANCE_FIELDS() not supported type ' % type)
        else:
            writer.write(bytearray(reader.read(5)))


def COUNTER(key):
    global counter
    counter.update({key: 1 + counter.get(key, 0)})


def decompress(reader, writer):
    instance = zlib.decompressobj()
    buffer = reader.read(1024 * 1024)
    while buffer:
        try:
            writer.write(instance.decompress(buffer))
        except:
            raise Exception('decompress failed')
        buffer = reader.read(1024 * 1024)
    writer.write(instance.flush())


def process(source, target):
    reader = None

    try:
        reader = open(source, 'rb')
        writer = open('.tailor', 'wb')
        decompress(reader, writer)
        reader.close()
        writer.close()
    except Exception as e:
        raise Exception('decompress failed at %d/%d: %s' % (reader.tell(), os.path.getsize(reader.name), str(e)))

    try:
        reader = open('.tailor', 'rb')
        writer = open(target, 'wb')
        if reader.read(18).decode('ascii') == 'JAVA PROFILE 6.0.1':
            decode(reader, writer)
        else:
            raise Exception('unknown file format!')
        reader.close()
        writer.close()
    except Exception as e:
        raise Exception('decode failed at %d/%d: %s' % (reader.tell(), os.path.getsize(reader.name), str(e)))


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

