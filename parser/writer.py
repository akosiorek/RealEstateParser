import logging

CSV_EXT = '.csv'
XLS_EXT = '.xlsx'

from classes import EntityExtractor

def findKeys(data, offset = 0):
    # logging.info('Starting')
    keys = {}
    for entry in data:
        key = entry[0]
        if not keys.has_key(key):
            keys[key] = offset + len(keys.keys())

    # logging.info('Returning keys: %s', keys)
    # logging.info('Returning')
    return keys

def findKeysList(data, access_method, offset = 0, top_level = True):
    if top_level:
        logging.info('Starting')

    keys = {}
    if isinstance(access_method, (tuple, list)) and len(access_method) == 1:
        access_method = access_method[0]

    for elem in data:
        if access_method and isinstance(access_method, (list, tuple)):
            partial_keys = findKeysList(access_method[0](elem), access_method[1:], 0, False)
        else:
            partial_keys = findKeys(access_method(elem))


        for key in partial_keys:
            if not keys.has_key(key):
                keys[key] = offset + len(keys.keys())

    # logging.info('Returning keys: %s', keys)
    if top_level:
        logging.info('Returning')
    return keys


def writeCSV(file, path):
    logging.info('Starting')
    logging.info('Finding keys')
    accesor = [lambda x: x.content]
    doc_keys = findKeysList(file.parts, accesor, 0)

    accesor.insert(0, lambda x:x.parts)
    estate_keys = findKeysList(file.parts, accesor, 0)

    accesor.insert(0, lambda x:x.parts)
    obj_headers = findKeysList(file.parts, accesor, 0)

    accesor[-1] = lambda x:x.parts
    obj_keys = findKeysList(file.parts, accesor, 0)

    doc_offset = 0
    estate_offset = len(doc_keys.keys())
    obj_offset = estate_offset + len(estate_keys.keys())
    key_num = obj_offset + len(obj_keys.keys())

    offsets = (doc_offset, estate_offset, obj_offset)
    keys = (doc_keys, estate_keys, obj_keys)

    row = ['',] * (key_num + 1)
    rows = [list(row),]

    logging.info('Preparing header')
    for keys, offset in zip(keys, offsets):
        for key in keys:
            rows[0][offset + keys[key]] = key

    rows[0][-1] = 'Typ'

    logging.info('Preparing document')
    for doc in file.parts:
        for estate in doc.parts:
            for obj in estate.parts:
                current_row = list(row)
                for line in doc.content:
                    current_row[doc_keys[line[0]] + doc_offset] = line[1].strip()

                for line in estate.content:
                    current_row[estate_keys[line[0]] + estate_offset] = line[1].strip()

                for line in obj.content:
                    current_row[-1] = line[0].strip()

                for line in obj.parts:
                    current_row[obj_keys[line[0]] + obj_offset] = line[1].strip()

                rows.append(current_row)

    logging.info('Dumping into %s', path + CSV_EXT)
    with open(path + CSV_EXT, 'w') as file:
        for row in rows:
            row = [elem.encode('utf-8') for elem in row]
            file.write('|'.join(row))
            file.write('\n')
    logging.info('Finished')

def writeXLS(file, path):
    logging.info('Starting')
    import xlsxwriter

    logging.info('Creating workbook at %s', path + XLS_EXT)
    workbook = xlsxwriter.Workbook(path + XLS_EXT)
    worksheet = workbook.add_worksheet()

    logging.info('Finding keys')
    accesor = [lambda x: x.content]
    doc_keys = findKeysList(file.parts, accesor, 0)

    accesor.insert(0, lambda x:x.parts)
    estate_keys = findKeysList(file.parts, accesor, 0)

    accesor.insert(0, lambda x:x.parts)
    accesor[-1] = lambda x:x.parts
    obj_keys = findKeysList(file.parts, accesor, 0)

    extractor = EntityExtractor(set(obj_keys))

    doc_offset = 0
    estate_offset = len(doc_keys.keys())
    obj_offset = estate_offset + len(estate_keys.keys())
    key_num = obj_offset + len(obj_keys.keys())

    offsets = (doc_offset, estate_offset, obj_offset)
    keys = (doc_keys, estate_keys, obj_keys)

    logging.info('Dumping data')
    typ_column = 0
    for keys, offset in zip(keys, offsets):
        typ_column += len(keys.keys())
        for key in keys:
            worksheet.write(0, keys[key] + offset, key)
    worksheet.write(0, typ_column, 'Typ')
    worksheet.freeze_panes(1, 0)

    row_count = 1
    for doc in file.parts:
        doc_line = row_count

        for estate in doc.parts:
            estate_line = row_count

            for obj in estate.parts:

                # current_type =
                # worksheet.write(row_count, typ_column, obj.content[0][0].strip())

                entities = extractor.extract(obj.parts)
                for entity in entities:
                    for key in entity:
                        worksheet.write(row_count, obj_keys[key] + obj_offset, entity[key])

                    worksheet.write(row_count, typ_column, obj.content[0][0].strip())
                    row_count += 1

            #merge estate cells
            for line in estate.content:
                col = estate_keys[line[0]] + estate_offset
                if estate_line != row_count - 1:
                    worksheet.merge_range(estate_line, col, row_count - 1, col, line[1].strip())
                else:
                    worksheet.write(estate_line, col, line[1].strip())

        #merge doc cells
        for line in doc.content:
            col = doc_keys[line[0]] + doc_offset
            if doc_line != row_count - 1:
                worksheet.merge_range(doc_line, col, row_count - 1, col, line[1].strip())
            else:
                worksheet.write(doc_line, col, line[1].strip())

    workbook.close()
    logging.info('Finished')