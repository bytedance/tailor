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

counter = {}


def verify(reader):
    LOGGER('HEADER', 'protocol: %s' % reader.read(19).decode('ascii'))
    LOGGER('HEADER', 'indentify: %d' % int.from_bytes(reader.read(4), byteorder='big', signed=False))
    LOGGER('HEADER', 'timestamp: %d' % int.from_bytes(reader.read(8), byteorder='big', signed=False))

    length = os.path.getsize(reader.name)
    while reader.tell() < length:
        tag = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        if tag == 0x01:    # STRING
            verify_STRING(reader)
        elif tag == 0x02:  # LOAD_CLASS
            verify_LOAD_CLASS(reader)
        elif tag == 0x03:  # UNLOAD_CLASS
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x04:  # STACK_FRAME
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x05:  # STACK_TRACE
            verify_STACK_TRACE(reader)
        elif tag == 0x06:  # ALLOC_SITES
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x07:  # HEAP_SUMMARY
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0A:  # START_THREAD
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0B:  # END_THREAD
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0C:  # HEAP_DUMP
            verify_HEAP_DUMP_SEGMENT(reader)
        elif tag == 0x0D:  # CPU_SAMPLES
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x0E:  # CONTROL_SETTINGS
            raise Exception('Not supported tag: %d' % tag)
        elif tag == 0x1C:  # HEAP_DUMP_SEGMENT
            verify_HEAP_DUMP_SEGMENT(reader)
        elif tag == 0x2C:  # HEAP_DUMP_END
            verify_HEAP_DUMP_END(reader)
        else:
            raise Exception('Not supported tag: %d, length: %d' % (tag, reader.tell()))


def verify_STRING(reader):
    COUNTER('STRING')
    LOGGER('STRING', 'tag: 0x01')
    LOGGER('STRING', 'timestamp: %d ' % int.from_bytes(reader.read(4), byteorder='big', signed=False))
    length = int.from_bytes(reader.read(4), byteorder='big', signed=False) - 4
    LOGGER('STRING', 'length: %d' % length)
    LOGGER('STRING', 'ID for this string: 0x%s ' % reader.read(4).hex())
    LOGGER('STRING', 'value: %s' % reader.read(length).decode('ascii'))


def verify_LOAD_CLASS(reader):
    COUNTER('LOAD_CLASS')
    LOGGER('LOAD-CLASS', 'tag: 0x02')
    LOGGER('LOAD-CLASS', 'timestamp: %d ' % int.from_bytes(reader.read(4), byteorder='big', signed=False))
    LOGGER('LOAD-CLASS', 'length: %d ' % int.from_bytes(reader.read(4), byteorder='big', signed=False))
    LOGGER('LOAD-CLASS', 'class serial number: 0x%s ' % reader.read(4).hex())
    LOGGER('LOAD-CLASS', 'class object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('LOAD-CLASS', 'stack trace serial number: 0x%s ' % reader.read(4).hex())
    LOGGER('LOAD-CLASS', 'class name string ID: 0x%s ' % reader.read(4).hex())


def verify_STACK_TRACE(reader):
    COUNTER('STACK_TRACE')
    LOGGER('STACK-TRACE', 'tag: 0x05')
    LOGGER('STACK-TRACE', 'timestamp: %d ' % int.from_bytes(reader.read(4), byteorder='big', signed=False))
    LOGGER('STACK-TRACE', 'length: %d ' % int.from_bytes(reader.read(4), byteorder='big', signed=False))
    LOGGER('STACK-TRACE', 'serial number: 0x%s ' % reader.read(4).hex())
    LOGGER('STACK-TRACE', 'thread serial number: 0x%s ' % reader.read(4).hex())

    length = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    LOGGER('STACK-TRACE', 'number of frames: %d ' % length)
    reader.seek(4 * length, 1)


def verify_HEAP_DUMP_SEGMENT(reader):
    COUNTER('HEAP_DUMP_SEGMENT')
    LOGGER('HEAP-DUMP-SEGMENT', 'tag: 0x1C')
    LOGGER('HEAP-DUMP-SEGMENT', 'timestamp: %d ' % int.from_bytes(reader.read(4), byteorder='big', signed=False))

    length = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    LOGGER('HEAP-DUMP-SEGMENT', 'length: %d ' % length)

    available = length
    while available > 0:
        available += reader.tell()

        tag = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        reader.seek(-1, 1)

        if tag == 0x01:    # ROOT_JNI_GLOBAL
            verify_ROOT_JNI_GLOBAL(reader)
        elif tag == 0x02:  # ROOT_JNI_LOCAL
            verify_ROOT_JNI_LOCAL(reader)
        elif tag == 0x03:  # ROOT_JAVA_FRAME
            verify_ROOT_JAVA_FRAME(reader)
        elif tag == 0x04:  # ROOT_NATIVE_STACK
            verify_ROOT_NATIVE_STACK(reader)
        elif tag == 0x05:  # ROOT_STICKY_CLASS
            verify_ROOT_STICKY_CLASS(reader)
        elif tag == 0x06:  # ROOT_THREAD_BLOCK
            verify_ROOT_THREAD_BLOCK(reader)
        elif tag == 0x07:  # ROOT_MONITOR_USED
            verify_ROOT_MONITOR_USED(reader)
        elif tag == 0x08:  # ROOT_THREAD_OBJECT
            verify_ROOT_THREAD_OBJECT(reader)
        elif tag == 0x20:  # ROOT_CLASS_DUMP
            verify_CLASS_DUMP(reader)
        elif tag == 0x21:  # ROOT_INSTANCE_DUMP
            verify_INSTANCE_DUMP(reader)
        elif tag == 0x22:  # OBJECT_ARRAY_DUMP
            verify_OBJECT_ARRAY_DUMP(reader)
        elif tag == 0x23:  # PRIMITIVE_ARRAY_DUMP
            verify_PRIMITIVE_ARRAY_DUMP(reader)
        elif tag == 0x89:  # ROOT_INTERNED_STRING
            verify_ROOT_INTERNED_STRING(reader)
        elif tag == 0x8A:  # ROOT_FINALIZING
            verify_ROOT_FINALIZING(reader)
        elif tag == 0x8B:  # ROOT_DEBUGGER
            verify_ROOT_DEBUGGER(reader)
        elif tag == 0x8C:  # ROOT_REFERENCE_CLEANUP
            verify_ROOT_REFERENCE_CLEANUP(reader)
        elif tag == 0x8D:  # ROOT_VM_INTERNAL
            verify_ROOT_VM_INTERNAL(reader)
        elif tag == 0x8E:  # ROOT_JNI_MONITOR
            verify_ROOT_JNI_MONITOR(reader)
        elif tag == 0x90:  # ROOT_UNREACHABLE
            raise Exception('verify_HEAP_DUMP_SEGMENT >>> Not supported tag: %d' % tag)
        elif tag == 0xC3:  # ROOT_PRIMITIVE_ARRAY_NODATA
            raise Exception('verify_HEAP_DUMP_SEGMENT >>> Not supported tag: %d' % tag)
        elif tag == 0xFE:  # ROOT_HEAP_DUMP_INFO
            verify_HEAP_DUMP_INFO(reader)
        elif tag == 0xFF:  # ROOT_UNKNOWN
            verify_ROOT_UNKNOWN(reader)
        else:
            raise Exception('Not supported tag: %d, length: %d' % tag, reader.tell())
        available -= reader.tell()


def verify_HEAP_DUMP_END(reader):
    reader.seek(8, 1)

    global counter
    print(counter)
    print('COMPLETE: %d -> %d ' % (reader.tell(), os.path.getsize(reader.name)))


def verify_ROOT_JNI_GLOBAL(reader):
    COUNTER('ROOT_JNI_GLOBAL')
    LOGGER('ROOT-JNI-GLOBAL', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-JNI-GLOBAL', 'object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-JNI-GLOBAL', 'JNI global ref ID: 0x%s ' % reader.read(4).hex())


def verify_ROOT_JNI_LOCAL(reader):
    COUNTER('ROOT_JNI_LOCAL')
    LOGGER('ROOT-JNI-LOCAL', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-JNI-LOCAL', 'object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-JNI-LOCAL', 'thread serial number: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-JNI-LOCAL', 'frame number in stack trace: 0x%s ' % reader.read(4).hex())


def verify_ROOT_JAVA_FRAME(reader):
    COUNTER('ROOT_JAVA_FRAME')
    LOGGER('ROOT-JAVA-FRAME', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-JAVA-FRAME', 'object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-JAVA-FRAME', 'thread serial number: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-JAVA-FRAME', 'frame number in stack trace: 0x%s ' % reader.read(4).hex())


def verify_ROOT_NATIVE_STACK(reader):
    COUNTER('ROOT_NATIVE_STACK')
    LOGGER('ROOT-NATIVE-STACK', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-NATIVE-STACK', 'object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-NATIVE-STACK', 'thread serial number: 0x%s ' % reader.read(4).hex())


def verify_ROOT_STICKY_CLASS(reader):
    COUNTER('ROOT_STICKY_CLASS')
    LOGGER('ROOT-STICKY-CLASS', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-STICKY-CLASS', 'object ID: 0x%s ' % reader.read(4).hex())


def verify_ROOT_THREAD_BLOCK(reader):
    COUNTER('ROOT_THREAD_BLOCK')
    LOGGER('ROOT-THREAD-BLOCK', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-THREAD-BLOCK', 'object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-THREAD-BLOCK', 'thread serial number: 0x%s ' % reader.read(4).hex())


def verify_ROOT_MONITOR_USED(reader):
    COUNTER('ROOT_MONITOR_USED')
    LOGGER('ROOT-MONITOR-USED', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-MONITOR-USED', 'object ID: 0x%s ' % reader.read(4).hex())


def verify_ROOT_THREAD_OBJECT(reader):
    COUNTER('ROOT_THREAD_OBJECT')
    LOGGER('ROOT-THREAD-OBJECT', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-THREAD-OBJECT', 'thread object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-THREAD-OBJECT', 'thread serial number: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-THREAD-OBJECT', 'stack trace serial number: 0x%s ' % reader.read(4).hex())


def verify_CLASS_DUMP(reader):
    COUNTER('CLASS_DUMP')
    LOGGER('CLASS-DUMP', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('CLASS-DUMP', 'class object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('CLASS-DUMP', 'stack trace serial number: 0x%s ' % reader.read(4).hex())
    LOGGER('CLASS-DUMP', 'super class object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('CLASS-DUMP', 'class loader object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('CLASS-DUMP', 'signers object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('CLASS-DUMP', 'protection domain object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('CLASS-DUMP', 'reserved: 0x%s ' % reader.read(4).hex())
    LOGGER('CLASS-DUMP', 'reserved: 0x%s ' % reader.read(4).hex())

    instance_size = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    LOGGER('CLASS-DUMP', 'instance size (in bytes): %d ' % instance_size)

    constant_fields_count = int(reader.read(2).hex(), 16)
    LOGGER('CLASS-DUMP', 'constant fields: %d, %s ' % (constant_fields_count, verify_CLASS_CONSTANT_FIELDS(reader, constant_fields_count)))

    static_fields_count = int(reader.read(2).hex(), 16)
    LOGGER('CLASS-DUMP', 'static fields: %d, %s ' % (static_fields_count, verify_CLASS_STATIC_FIELDS(reader, static_fields_count)))

    instance_fields_count = int(reader.read(2).hex(), 16)
    LOGGER('CLASS-DUMP', 'instance fields: %d, %s ' % (instance_fields_count, verify_CLASS_INSTANCE_FIELDS(reader, instance_fields_count)))


def verify_INSTANCE_DUMP(reader):
    COUNTER('INSTANCE_DUMP')
    LOGGER('INSTANCE-DUMP', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('INSTANCE-DUMP', 'object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('INSTANCE-DUMP', 'stack trace serial number: 0x%s ' % reader.read(4).hex())
    LOGGER('INSTANCE-DUMP', 'class object ID: 0x%s ' % reader.read(4).hex())

    bytes_followed = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    LOGGER('INSTANCE-DUMP', 'number of bytes that followed: %d ' % bytes_followed)
    reader.seek(bytes_followed, 1)


def verify_OBJECT_ARRAY_DUMP(reader):
    COUNTER('OBJECT_ARRAY_DUMP')
    LOGGER('OBJECT-ARRAY-DUMP', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('OBJECT-ARRAY-DUMP', 'array object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('OBJECT-ARRAY-DUMP', 'stack trace serial number: 0x%s ' % reader.read(4).hex())

    length = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    LOGGER('OBJECT-ARRAY-DUMP', 'number of elements: %d ' % length)

    LOGGER('OBJECT-ARRAY-DUMP', 'array class object ID: 0x%s ' % reader.read(4).hex())

    LOGGER('OBJECT-ARRAY-DUMP', 'elements: %s ' % verify_OBJECT_ARRAY_ELEMENTS(reader, length))


def verify_PRIMITIVE_ARRAY_DUMP(reader):
    COUNTER('PRIMITIVE_ARRAY_DUMP')
    LOGGER('PRIMITIVE-ARRAY-DUMP', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('PRIMITIVE-ARRAY-DUMP', 'array object ID: 0x%s ' % reader.read(4).hex())
    LOGGER('PRIMITIVE-ARRAY-DUMP', 'stack trace serial number: 0x%s ' % reader.read(4).hex())

    length = int.from_bytes(reader.read(4), byteorder='big', signed=False)
    LOGGER('PRIMITIVE-ARRAY-DUMP', 'number of elements: %d ' % length)

    type = int.from_bytes(reader.read(1), byteorder='big', signed=False)
    LOGGER('PRIMITIVE-ARRAY-DUMP', 'element type: %d ' % type)

    LOGGER('PRIMITIVE-ARRAY-DUMP', 'elements: %s ' % verify_PRIMITIVE_ARRAY_ELEMENTS(reader, type, length))


def verify_ROOT_INTERNED_STRING(reader):
    COUNTER('ROOT_INTERNED_STRING')
    LOGGER('ROOT-INTERNED-STRING', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-INTERNED-STRING', 'object ID: 0x%s ' % reader.read(4).hex())


def verify_ROOT_FINALIZING(reader):
    COUNTER('ROOT_FINALIZING')
    LOGGER('ROOT_FINALIZING', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT_FINALIZING', 'object ID: 0x%s ' % reader.read(4).hex())


def verify_ROOT_DEBUGGER(reader):
    COUNTER('ROOT_DEBUGGER')
    LOGGER('ROOT-DEBUGGER', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-DEBUGGER', 'object ID: 0x%s ' % reader.read(4).hex())


def verify_ROOT_REFERENCE_CLEANUP(reader):
    COUNTER('ROOT_REFERENCE_CLEANUP')
    LOGGER('ROOT_REFERENCE_CLEANUP', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT_REFERENCE_CLEANUP', 'object ID: 0x%s ' % reader.read(4).hex())


def verify_ROOT_VM_INTERNAL(reader):
    COUNTER('ROOT_VM_INTERNAL')
    LOGGER('ROOT-VM-INTERNAL', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-VM-INTERNAL', 'object ID: 0x%s ' % reader.read(4).hex())


def verify_ROOT_JNI_MONITOR(reader):
    COUNTER('ROOT_JNI_MONITOR')
    LOGGER('ROOT-JNI-MONITOR', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-JNI-MONITOR', 'string id: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-JNI-MONITOR', 'thread serial number: 0x%s ' % reader.read(4).hex())
    LOGGER('ROOT-JNI-MONITOR', 'stack trace serial number: 0x%s ' % reader.read(4).hex())


def verify_HEAP_DUMP_INFO(reader):
    COUNTER('HEAP_DUMP_INFO')
    LOGGER('HEAP-DUMP-INFO', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('HEAP-DUMP-INFO', 'heap ID: 0x%s ' % reader.read(4).hex())
    LOGGER('HEAP-DUMP-INFO', 'heap name ID: 0x%s ' % reader.read(4).hex())


def verify_ROOT_UNKNOWN(reader):
    COUNTER('ROOT_UNKNOWN')
    LOGGER('ROOT-UNKNOWN', 'tag: 0x%s ' % reader.read(1).hex())
    LOGGER('ROOT-UNKNOWN', 'object ID: 0x%s ' % reader.read(4).hex())


def verify_OBJECT_ARRAY_ELEMENTS(reader, length):
    reader.seek(4 * length, 1)
    return []


def verify_PRIMITIVE_ARRAY_ELEMENTS(reader, type, length):
    if type >= 12 or type == 3 or type <= 1:
        raise Exception('verify_PRIMITIVE_ARRAY_ELEMENTS >>> Not supported type: %d ' % type)
    elif type == 2:     # object
        reader.seek(4 * length, 1)
    elif type == 4:     # boolean
        reader.seek(1 * length, 1)
    elif type == 5:     # char
        reader.seek(2 * length, 1)
    elif type == 6:     # float
        reader.seek(4 * length, 1)
    elif type == 7:     # double
        reader.seek(8 * length, 1)
    elif type == 8:     # byte
        reader.seek(1 * length, 1)
    elif type == 9:     # short
        reader.seek(2 * length, 1)
    elif type == 10:    # int
        reader.seek(4 * length, 1)
    elif type == 11:    # long
        reader.seek(8 * length, 1)
    else:
        raise Exception('verify_PRIMITIVE_ARRAY_ELEMENTS >>> Not supported type: %d ' % type)
    return []


def verify_CLASS_CONSTANT_FIELDS(reader, count):
    while count > 0:
        count -= 1

        reader.seek(2, 1)

        type = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        if type >= 12 or type == 3 or type <= 1:
            raise Exception('verify_CLASS_CONSTANT_FIELDS() not supported type ' % type)
        elif type == 2:   # object
            reader.seek(4, 1)
        elif type == 4:   # boolean
            reader.seek(1, 1)
        elif type == 5:   # char
            reader.seek(2, 1)
        elif type == 6:   # float
            reader.seek(4, 1)
        elif type == 7:   # double
            reader.seek(8, 1)
        elif type == 8:   # byte
            reader.seek(1, 1)
        elif type == 9:   # short
            reader.seek(2, 1)
        elif type == 10:  # int
            reader.seek(4, 1)
        elif type == 11:  # long
            reader.seek(8, 1)
        else:
            raise Exception('verify_CLASS_CONSTANT_FIELDS() not supported type ' % type)
    ################################################################################
    return []


def verify_CLASS_STATIC_FIELDS(reader, count):
    while count > 0:
        count -= 1

        reader.seek(4, 1)

        type = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        if type >= 12 or type == 3 or type <= 1:
            raise Exception('verify_CLASS_STATIC_FIELDS() not supported type ' % type)
        elif type == 2:   # object
            reader.seek(4, 1)
        elif type == 4:   # boolean
            reader.seek(1, 1)
        elif type == 5:   # char
            reader.seek(2, 1)
        elif type == 6:   # float
            reader.seek(4, 1)
        elif type == 7:   # double
            reader.seek(8, 1)
        elif type == 8:   # byte
            reader.seek(1, 1)
        elif type == 9:   # short
            reader.seek(2, 1)
        elif type == 10:  # int
            reader.seek(4, 1)
        elif type == 11:  # long
            reader.seek(8, 1)
        else:
            raise Exception('verify_CLASS_STATIC_FIELDS() not supported type ' % type)
    return []


def verify_CLASS_INSTANCE_FIELDS(reader, count):
    while count > 0:
        count -= 1

        reader.seek(4, 1)

        type = int.from_bytes(reader.read(1), byteorder='big', signed=False)
        if type >= 12 or type == 3 or type <= 1:
            raise Exception('verify_CLASS_INSTANCE_FIELDS() not supported type ' % type)
    return []


def COUNTER(key):
    global counter
    counter.update({key: 1 + counter.get(key, 0)})


def process(source):
    try:
        stream = open(source, 'rb')
        verify(stream)
        stream.close()
    except Exception as e:
        print(e)


def LOGGER(tag, string):
    if False:
        print('%s >>> %s' % (tag, string))


if __name__ == '__main__':
    argParser = argparse.ArgumentParser()
    argParser.add_argument('-i', '--input', help='input file name')
    args = argParser.parse_args()

    if not args.input:
        raise Exception('ERROR: input file name should not be null, using -h or --help for detail')

    process(args.input)

