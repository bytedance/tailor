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

#ifndef STREAM_H
#define STREAM_H 1

#include <stdlib.h>
//**************************************************************************************************
#define LENGTH 8 * 1024

struct Reader {
	virtual ~Reader() {}
	virtual bool isAvailable() = 0;

	char * buffer;
	size_t length;
	size_t offset;
};

struct Writer {
	virtual ~Writer() {}
	virtual  int proxy(int flags) = 0;
	virtual void flush(char *buff, size_t bytes, bool isEof) = 0;

	const char *name;
	int wrap;

	FILE * target;
	char   buffer[LENGTH];
	size_t offset;
};
//**************************************************************************************************
inline void fill(Writer *writer, char value) {
	if (writer->offset + 1 > LENGTH) {
		writer->flush(writer->buffer, writer->offset, false);
		writer->offset = 0;
	}

	writer->buffer[writer->offset++] = value;
}

inline void fill(Writer *writer, char *array, size_t count) {
	if (writer->offset + count > LENGTH) {
		writer->flush(writer->buffer, writer->offset, false);
		writer->offset = 0;
	}

	for (int i = 0; i < count; i++) {
		writer->buffer[writer->offset++] = array[i];
	}
}

inline void fill(Writer *writer, Reader *reader, size_t count) {
	if (writer->offset + count > LENGTH) {
		writer->flush(writer->buffer, writer->offset, false);
		writer->offset = 0;
	}

	for (int i = 0; i < count; i++) {
		writer->buffer[writer->offset++] = reader->buffer[reader->offset++];
	}
}

inline void copy(Writer *writer, Reader *reader, size_t count) {
	if (writer->offset > 0) {
		writer->flush(writer->buffer, writer->offset, false);
		writer->offset = 0;
	}

	writer->flush(reader->buffer + reader->offset, count, false);
	reader->offset += count;
}
//**************************************************************************************************
#endif //STREAM_H