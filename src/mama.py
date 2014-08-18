#!/usr/bin/env python
# -*- coding: Windows-1250 -*-

DEBUG = False
DEBUG = True


sep = ':'

DOCUMENT = "DOCUMENT"
ESTATE = "ESTATE"
SEPARATORS = [DOCUMENT, ESTATE]

def printArr(arr):	
    for a in arr:
        print a

def findKeys(data, offset = 0):
    keys = {}
    for entry in data:
        for line in entry:
            key = line[0]
            if not keys.has_key(key):
                keys[key] = offset + len(keys.keys())
    return keys


def getFilepaths():
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
    doc_sep  = '====================================================================== :'
    estate_sep = '---------------------------------------------------------------------- :'
    separators = [sep, doc_sep, estate_sep, DOCUMENT, ESTATE]

    text = re.sub('  +', '', text)
    text = text.replace(doc_sep, DOCUMENT).replace(estate_sep, ESTATE)
    text = [line.strip() for line in text.split('\n') if line.strip()]

    return text



def main():
    input_file, output_file = getFilepaths()

    with open(input_file, 'r') as file:
        text = file.read()
    text = prepareData(text)

    # extract global document's id
    globalId = text[0]
    text = text[1:]

    # deal with multi-line values:
    # every lines spllited by sep should have 2 elements or be empty
    # if a line has a single element it belongs to a preceeding line of 2 elements
    tmp_text = []
    for line in text:
        line = line.strip()
        splitted = line.split(sep)
        if len(splitted) == 2 or splitted[0] == '' or line in SEPARATORS:
            tmp_text.append(line)
        elif tmp_text and line not in SEPARATORS:
            tmp_text[-1] += ' ' + line[0]
    text = tmp_text

    # if DEBUG:
    #     counter = 0
    #     for line in text:
    #         line = line.strip().split(sep)
    #         print len(line), line, counter
    #         counter += 1
    #         assert (len(line) >= 1 or line[0] in SEPARATORS)

    # rebuild document structure; needed for splitting by different seps
    text = '\n'.join(tmp_text).strip()
    documents = text.split(DOCUMENT)

    # we'll treat the input file as a list of documents
    # each document has a header and a list of real_estates
    # extract doc_headers and real_estates and save them in lists with matching indices
    doc_headers = []
    real_estates = []
    for document in documents:
        document = document.strip().split('\n')

        counter = 0
        while counter < len(document) and document[counter]:
            counter += 1

        doc_headers.append([line.split(sep) for line in document[:counter]])

        # eradicate empty string created by split
        estate_pack = []
        for estate in '\n'.join(document[counter:]).strip().split(ESTATE):
         if estate:
             estate_pack.append(estate)
        if estate_pack:
          real_estates.append(estate_pack)


    # ## DEBUG
    # for header in doc_headers:
    #     printArr(header)
    print ''
    print 'doc_headers'
    for key in findKeys(doc_headers):
        print key

    ## DEBUG
    # print ''
    # for estate in real_estates:
    #     printArr(estate)

    # # real_estates are now a block of file per document
    # # we have to tokenize them and save appropriately
    # # estate_data contain estate doc_headers
    # # prop_packs contain lists of properties for each estate
    # estate_data = []
    # prop_packs = []
    # for estate in real_estates:
    #     # print estate
    #     estate_header = []
    #     for line in estate[0].split('\n'):
    #           estate_header.append([part.strip() for part in line.split(sep)])
    #
    #     # print estate_header
    #
    #     formatted_estate = []
    #     estate_data.append(formatted_estate)
    #
    #     prop = False
    #     for line in estate_header:
    #         if line == ['']:
    #             continue
    #         if len(line) == 2 and not line[1]:
    #             prop = True
    #
    #         if not prop:
    #                 formatted_estate.append(line)
    #         elif len(line) == 2 and not line[1]:
    #             prop_entry = [['Typ', line[0]]]
    #             prop_packs.append(prop_entry)
    #         else:
    #             prop_entry.append(line)
    #
    # # for estate in estate_data:
    # #     print ''
    # #     printArr(estate)
    #
    # header_keys = findKeys(doc_headers, 0)
    # offset = len(header_keys.keys())
    # document_keys = findKeys(estate_data, offset)
    # offset += len(document_keys.keys())
    # prop_keys = findKeys(prop_packs, offset)

    #print header_keys
    # print document_keys
    #print prop_keys

    # key_map = dict(header_keys.items() + document_keys.items() + prop_keys.items())
    # key_num = len(key_map.keys())
    # print key_map


    # counter = 0
    # for pack in prop_packs:
    #     counter += len(pack)
    #
    # row = ['',] * key_num
    # rows = [list(row),]
    #
    # for key in key_map:
    #     rows[0][key_map[key]] = key
    #
    # print rows
    #
    # for head, doc, pack in zip(doc_headers, estate_data, prop_packs):
    #     for props in pack:
    #         entry = list(row)
    #         rows.append(entry)
    #         print ''
    #         print doc
    #         print ''
    #
    #         for pair in head + doc + pack:
    #             entry[key_map[pair[0]]] = pair[1]
    #
    # print rows
    #
    #
    # with open(output_file, 'w') as file:
    #     for row in rows:
    #         file.write(','.join(row))
    #         file.write('\n')




if __name__ == '__main__':
    main()
