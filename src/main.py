#!/usr/bin/env python
# -*- coding: Windows-1250 -*-

from writer_old import *
from config import *
from classes import *

import re
import logging

DEBUG = False
# DEBUG = True


def getFilepaths():
    if DEBUG:
        from os import path
        input_file = path.dirname(path.realpath(__file__)) + '/../data/gm.txt'
    else:
        import tkFileDialog
        input_file = tkFileDialog.askopenfilename()
    output_file = re.match(r'(.*)\.(.*)', input_file).groups()[-2] + FORMATED_POSTFIX

    logging.info('Returning %s, %s', input_file, output_file)
    return input_file, output_file

def prepareData(text):
    logging.info('Preparing data')

    text = text\
        .replace(doc_sep, DOCUMENT)  \
        .replace(estate_sep, ESTATE) \
        .replace(' :', SEP)

    text = re.sub(SEP + ' ^( )', ':', text)
    text = re.sub(' *' + SEP + ' *', SEP, text)
    text = re.sub(SEP + ' ?' + SEP, SEP, text)
    logging.info('Replaced white characters')

    counted_spaces_text = []
    for line in text.split('\n')[:]:
        # Change encoding to utf-8
        line = line.decode('windows-1250')

        # deal with multi-line values
        # tackles the most obvious cases only
        if counted_spaces_text and line.strip() and len(line.split(SEP, 1)) != 2 and (not line.strip() in SEPARATORS):
            counted_spaces_text[-1][1] += re.sub('\s+', ' ', line)
        else:
           counted_spaces_text\
            .append([len(line) - len(line.lstrip(' ')), line.strip()])

    logging.info('Elimnated multi-line values')

    while counted_spaces_text[0][1] == '':
        del counted_spaces_text[0]

    while counted_spaces_text[-1][1] == '':
        del counted_spaces_text[-1]

    logging.info('Returning')
    return counted_spaces_text

def main(input_file, output_file):
    with open(input_file, 'r') as file:
        text = file.read()

    text = prepareData(text)

    file = Document()
    file.content = text[0][1]
    text = text[1:]
    text[0] = [0, DOCUMENT]

    mode = ''
    doc_indent = -1
    estate_indent = -1
    obj_indent = -1

    OBJ = False

    logging.info('Building document tree')
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
            file.recent_doc().parts.append(Document())
            estate_indent = -1
            mode = ESTATE
            obj_indent = -1
            OBJ = False

        # Process data
        elif mode == DOCUMENT:
            logging.debug('Mode: Document')
            if doc_indent == -1:
                doc_indent = indent

            if line[0] == doc_indent:
                # print string
                file.recent_doc().content.append(string)
            else:
                logging.debug('Mode: Estate')
                estate = Document()
                estate.content.append(string)
                file.recent_doc().parts.append(estate)
                estate_indent = -1
                mode = ESTATE
                OBJ = False
                continue

        elif mode == ESTATE:
            logging.debug('Mode: Estate')
            if estate_indent == -1:
                estate_indent = indent

            if indent == estate_indent:
                splitted = string.split(SEP)
                if len(splitted) == 2 and splitted[1].strip():
                    file.recent_estate().content.append(string)
                else:
                    obj = Document()
                    obj.content.append(string)
                    file.recent_estate().parts.append(obj)
                    OBJ = True
            elif OBJ:
                logging.debug('Mode: Object')
                if obj_indent == -1:
                    obj_indent = indent

                if indent != obj_indent:
                    file.recent_obj().content[-1] += string.replace(SEP, key_value_sep)
                else:
                    file.recent_obj().parts.append(string)
            else:
                if indent != estate_indent:
                    file.recent_estate().content[-1] += string.replace(SEP, key_value_sep)


    logging.info('Line-splitting document tree')
    file.line_split(SEP)

    #writeCSV(file, output_file)
    writeXLS(file, output_file)



if __name__ == '__main__':
    FORMAT = "[%(filename)s:%(lineno)s:%(funcName)10s:%(levelname)s] %(message)s"
    logging.basicConfig(format=FORMAT, filename='src.log', level=logging.INFO)
    logging.info('Start')

    input_file, output_file = getFilepaths()

    main(input_file, output_file)
    logging.info('Finished')