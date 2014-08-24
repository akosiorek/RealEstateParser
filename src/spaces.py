#!/usr/bin/env python
# -*- coding: Windows-1250 -*-

DEBUG = False
DEBUG = True


sep = ':'

OBJECT = "!OBJECT!"
DOCUMENT = "!DOCUMENT!"
ESTATE = "!ESTATE!"
SEP = "!SEPARATOR!"
SEPARATORS = [SEP, DOCUMENT, ESTATE]
NIERUCHOMOSC = 'Nieru'

doc_sep  = '====================================================================== :'
estate_sep = '---------------------------------------------------------------------- :'

class Document(object):


    def __init__(self):
        self.header = []
        self.parts = []

def current_doc(file):
    return file.parts[-1]

def current_estate(file):
    return file.parts[-1].parts[-1]

def current_obj(file):
    return file.parts[-1].parts[-1].parts[-1]

def RecursiveSplit(file, sep):

    if isinstance(file.header, basestring):
        file.header = [part.strip() for part in file.header.split(sep)]
    else:
        for i in xrange(len(file.header)):
            file.header[i] = [part.strip() for part in file.header[i].split(sep)]

    if file.parts:
        if isinstance(file.parts[0], Document):
            for i in xrange(len(file.parts)):
                file.parts[i] = RecursiveSplit(file.parts[i], sep)
        else:
            for i in xrange(len(file.parts)):
                file.parts[i] = [part.strip() for part in file.parts[i].split(sep)]

    return file

def RecursiveCount(file):
    count = 0
    if file.parts and len(file.parts):
        if isinstance(file.parts[0], Document):
            for document in file.parts:
                    count += RecursiveCount(document)
        else:
            count += len(file.parts)
    return count



def printArr(arr):	
    for a in arr:
        print a



def findKeys(data, offset = 0):
    keys = {}
    for entry in data:
        key = entry[0]
        if not keys.has_key(key):
            keys[key] = offset + len(keys.keys())
    return keys

def findKeysList(data, access_method, offset = 0):
    keys = {}
    if isinstance(access_method, (tuple, list)) and len(access_method) == 1:
        access_method = access_method[0]

    for elem in data:
        if access_method and isinstance(access_method, (list, tuple)):
            partial_keys = findKeysList(access_method[0](elem), access_method[1:])
        else:
          partial_keys = findKeys(access_method(elem))


        for key in partial_keys:
            if not keys.has_key(key):
                keys[key] = offset + len(keys.keys())

    return keys

def getFilepaths():
    input_file = ''
    if DEBUG:
        from os import path
        input_file = path.dirname(path.realpath(__file__)) + '/../data/gm.txt'
    else:
        import tkFileDialog
        input_file = tkFileDialog.askopenfilename()
    output_file = input_file.split('.')[0] + '_formated.csv'
    return input_file, output_file

def prepareData(text):
    import re

    text = text\
        .replace(doc_sep, DOCUMENT)  \
        .replace(estate_sep, ESTATE) \
        .replace(' :', SEP)

    text = re.sub(SEP + ' ^( )', ':', text)
    text = re.sub(' *' + SEP + ' *', SEP, text)

    counted_spaces_text = []
    for line in text.split('\n')[:]:

        # deal with multi-line values
        # tackles the most obvious cases only
        if counted_spaces_text and line.strip() and len(line.split(SEP, 1)) != 2 and not line.strip() in SEPARATORS:
            counted_spaces_text[-1][1] += line
        else:
           counted_spaces_text\
            .append([len(line) - len(line.lstrip(' ')), line.strip()])

    while counted_spaces_text[0][1] == '':
        del counted_spaces_text[0]

    while counted_spaces_text[-1][1] == '':
        del counted_spaces_text[-1]

    return counted_spaces_text

def main():
    input_file, output_file = getFilepaths()

    with open(input_file, 'r') as file:
        text = file.read()
    text = prepareData(text)

    file = Document()
    file.header = text[0][1]
    text = text[1:]
    text[0] = [0, DOCUMENT]

    mode = ''
    doc_indent = -1
    estate_indent = -1
    obj_indent = -1

    OBJ = False

    for line in text[:]:
        # print line
        indent = line[0]
        string = line[1]
        if not string.strip():
            continue


        # Change processing mode
        if string == DOCUMENT:
            file.parts.append(Document())
            doc_indent = -1
            mode = DOCUMENT
        elif string == ESTATE:
            current_doc(file).parts.append(Document())
            estate_indent = -1
            mode = ESTATE
            obj_indent = -1
            OBJ = False

        # Process data
        elif mode == DOCUMENT:
            if doc_indent == -1:
                doc_indent = indent

            if line[0] == doc_indent:
                # print string
                current_doc(file).header.append(string)
            else:
                estate = Document()
                estate.header.append(string)
                current_doc(file).parts.append(estate)
                estate_indent = -1
                mode = ESTATE
                OBJ = False
                continue

        elif mode == ESTATE:
            if estate_indent == -1:
                estate_indent = indent

            if indent == estate_indent:
                splitted = string.split(SEP)
                if len(splitted) == 2 and splitted[1].strip():
                    current_estate(file).header.append(string)
                else:
                    obj = Document()
                    obj.header.append(string)
                    current_estate(file).parts.append(obj)
                    OBJ = True
            elif OBJ:
                if obj_indent == -1:
                    obj_indent = indent

                if indent != obj_indent:
                    current_obj(file).header[-1] += string.replace(SEP, sep)
                else:
                    current_obj(file).parts.append(string)
            else:
                if indent != estate_indent:
                    current_estate(file).header[-1] += string.replace(SEP, sep)


    RecursiveSplit(file, SEP)

    accesor = [lambda x: x.header]
    doc_keys = findKeysList(file.parts, accesor, 0)

    accesor = [lambda x:x.parts, lambda x:x.header]
    estate_keys = findKeysList(file.parts, accesor, 0)

    accesor = [lambda x:x.parts, lambda x:x.parts, lambda x:x.header]
    obj_headers = findKeysList(file.parts, accesor, 0)

    accesor = [lambda x:x.parts, lambda x:x.parts, lambda x:x.parts]
    obj_keys = findKeysList(file.parts, accesor, 0)

    doc_offset = 0
    estate_offset = len(doc_keys.keys())
    obj_offset = estate_offset + len(estate_keys.keys())
    key_num = obj_offset + len(obj_keys.keys())

    offsets = (doc_offset, estate_offset, obj_offset)
    keys = (doc_keys, estate_keys, obj_keys)


    # obj_count = RecursiveCount(file)

    row = ['',] * (key_num + 1)
    rows = [list(row),]

    for keys, offset in zip(keys, offsets):
        for key in keys:
            rows[0][offset + keys[key]] = key

    rows[0][-1] = 'Typ'

    print rows

    for doc in file.parts:
        for estate in doc.parts:
            for obj in estate.parts:
                current_row = list(row)
                for line in doc.header:
                    current_row[doc_keys[line[0]] + doc_offset] = line[1]

                for line in estate.header:
                    current_row[estate_keys[line[0]] + estate_offset] = line[1]

                for line in obj.header:
                    current_row[-1] = line[0]

                for line in obj.parts:
                    current_row[obj_keys[line[0]] + obj_offset] = line[1]
                    
                rows.append(current_row)

    print rows


    with open(output_file, 'w') as file:
        for row in rows:
            file.write(','.join(row))
            file.write('\n')




if __name__ == '__main__':
    main()
