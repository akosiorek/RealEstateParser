#!/usr/bin/env python
# -*- coding: Windows-1250 -*-

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


def main():
    import tkFileDialog

    DEBUG = True
    DEBUG = False

    #filename = tkFileDialog.askopenfilename()
    filename = '/home/adam/Desktop/gm.txt'
    output_file = filename.split('.')[0] + '_formated.csv'


    doc_sep = '====================================================================== :'
    estate_sep = '---------------------------------------------------------------------- :'
    sep = ':'


    with open(filename, 'r') as file:
        text = [line.strip() for line in file]

    globalId = text[0]

    tmp_text = []
    for line in text[1:]:
        line = line.strip()
        splitted = line.split(sep)
        if len(splitted) == 2 or splitted[0] == '':
            tmp_text.append(line)
        elif tmp_text and isinstance(tmp_text[-1], (list, tuple)):
            tmp_text[-1][-1] += line[0]

    text = '\n'.join(tmp_text).strip()
    # print text

    documents = text.split(doc_sep)

    headers = []
    estates = []
    for document in documents:
        document = document.strip().split('\n')

        counter = 0
        while document[counter]:
            counter += 1
        #
        # header = []
        # for line in document[:counter]:
        #     splitted = line.split(':')
        #     if len(splitted) == 2:
        #         header.append(splitted)
        #     elif header:
        #         header[-1][-1] += splitted[0]
        #
        # headers.append(header)
        headers.append(document[:counter])
        estates.append('\n'.join(document[counter:]).strip().split(estate_sep))

    for header in headers:
        printArr(header)
    print ''
    print 'headers'
    for key in findKeys(headers):
        print key

    # print ''
    # for estate in estates:
    # 	printArr(estate)
    # print ''
    # print 'keys'
    # for key in findKeys(estates):
    #     print key

    # formatted_estates = []
    # prop_packs = []
    # for estate in estates:
    # 	estate = [line.split(':') for line in estate[0].split('\n')]
    # 	formatted_estate = []
    # 	formatted_estates.append(formatted_estate)
    #
    # 	prop = False
    # 	for line in estate:
    # 		if line == ['']:
    # 			continue
    # 		if len(line) == 2 and not line[1]:
    # 			prop = True
    #
    # 		if not prop:
    # 			if len(line) == 1:
    # 				formatted_estate[-1][-1] += ' ' + line[0]
    # 			else:
    # 				formatted_estate.append(line)
    # 		elif len(line) == 2 and not line[1]:
    # 			prop_entry = [['Typ', line[0]]]
    # 			prop_packs.append(prop_entry)
    # 		else:
    # 			prop_entry.append(line)
    #
    # header_keys = findKeys(headers, 0)
    # offset = len(header_keys.keys())
    # document_keys = findKeys(formatted_estates, offset)
    # offset += len(document_keys.keys())
    # prop_keys = findKeys(prop_packs, offset)
    #
    #
    # key_map = dict(header_keys.items() + document_keys.items() + prop_keys.items())
    # key_num = len(key_map.keys())
    # print key_map
    #
    #
    # counter = 0
    # for pack in prop_packs:
    # 	counter += len(pack)
    #
    # row = ['',] * key_num
    # rows = [list(row),]
    #
    # for key in key_map:
    # 	rows[0][key_map[key]] = key
    #
    # print rows
    #
    # for head, doc, pack in zip(headers, formatted_estates, prop_packs):
    # 	for props in pack:
    # 		entry = list(row)
    # 		rows.append(entry)
    # 		print ''
    # 		print doc
    # 		print ''
    #
    # 		for pair in head + doc + pack:
    # 			entry[key_map[pair[0]]] = pair[1]
    #
    # print rows
    #
    #
    # with open(output_file, 'w') as file:
    # 	for row in rows:
    # 		file.write(','.join(row))
    # 		file.write('\n')




if __name__ == '__main__':
    main()
