__author__ = 'Adam Kosiorek'
# −*− coding: UTF−8 −*−

def findKeyset(data):
    keyset = set()
    for entry in data:
        print entry
        for key in entry.keys():
            keyset.add(key)
    return keyset


def writeXLS(data, path):
    pass

if __name__ == '__main__':
    import parser
    parser = parser.SpaceParser()
    with open('../data/gm.txt') as inputFile:
        parser.feed(inputFile)
    print findKeyset(parser.documents)

    subdocs = []
    budynki = []
    dzialki = []
    inne = []
    for entry in parser.documents:
        subdocs.extend(entry['SUBDOCUMENT'])
        try:
            budynki.extend(subdocs[-1]['Budynki'])
        except:
            pass
        try:
            dzialki.extend(subdocs[-1]['Dzia�ki'])
        except:
            pass


    print findKeyset(subdocs)
    print findKeyset(budynki)
    # print findKeyset(dzialki)