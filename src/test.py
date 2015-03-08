from parser import SpaceParser
# −*− coding: UTF−8 −*−

data = open('../data/gm.txt').read()
parser = SpaceParser(inputEncoding='Windows-1250', outputEncoding='utf-8')
parser.feed(data)
docs = parser.output()
# print len(docs), docs

budynki = u'Budynki'
dzialki = u'Dzia\u0142ki'
lokale = u'Lokale'

keys = (budynki, dzialki, lokale)

# parser.printDocument(docs)

for key in keys:
    print key
    for doc in docs:
        for subdoc in doc[SpaceParser.SUBDOCUMENT_KEY]:
            # print subdoc
            if key in subdoc:
                print subdoc[key]