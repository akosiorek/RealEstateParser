__author__ = 'Adam Kosiorek'
# −*− coding: UTF−8 −*−

import parser

import unittest
import os

projectDataFolder = os.path.join(os.path.join(os.getcwd(), os.pardir), os.pardir)
projectDataFolder = os.path.join(projectDataFolder, 'data/')
shortTestFile = os.path.join(projectDataFolder, 'test.txt')
longTestFile = os.path.join(projectDataFolder, 'gm.txt')
entityTestFile = os.path.join(projectDataFolder, 'entity_test.txt')

class BaseParserTest(unittest.TestCase):

    def setUp(self):
        self.shortInput = open(shortTestFile)
        self.shortText = open(shortTestFile).read()
        self.parser = parser.BaseParser()

    def tearDown(self):
        self.shortInput.close()

    def test_parseLine(self):
        text = self.shortText.split('\n')
        line0 = self.parser.parseLine(text[0])
        self.assertEqual(line0, ('tag', 'RCiWN dla 2814042 Dywity'))
        line3 = self.parser.parseLine(text[2])
        self.assertEqual(line3, ('Dokument             ','OA-810/2014 z dnia 2014.06.25'))

    def test_feedString(self):
        self.parser.feed(self.shortText)
        stringPieces = list(self.parser.pieces)
        self.parser.reset()
        self.parser.feed(self.shortInput)
        inputPieces = list(self.parser.pieces)
        self.assertEqual(stringPieces, inputPieces)


    def test_feed(self):
        self.parser.feed(self.shortInput)
        pieces = self.parser.pieces

        self.assertEqual(pieces[0], ('tag', 'RCiWN dla 2814042 Dywity'))
        self.assertEqual(pieces[1], ('tag', ''))
        self.assertEqual(pieces[2], ('Dokument             ','OA-810/2014 z dnia 2014.06.25'))
        self.assertEqual(pieces[-2], ('         adres(y)              ','BUKWA�D 58'))




#TODO write real tests
#   1) simple document as in test.txt
#   2) a set of documents with multiple values at each level
#   3) a document without some levels
#   4) a document with several same subdocuments without separation
class SpaceParserTest(unittest.TestCase):
    '''Document Structure:
        Header
            Property1=Value1
            ...
            SUBDOCUMENT:
                Property1=Value1
                ...
                Dzialki:
                    Property1=Value1
                    ...
                Nieruchomosci:
                    Property1=Value1
                    ...
                Lokale:
                    Property1=Value1
                    ...
                    Pomieszczenia przynalezne:
                        Property1=Value1
                        ...

    '''

    def setUp(self):
        self.shortInput = open(shortTestFile)
        self.shortText = open(shortTestFile).read()
        self.parser = parser.SpaceParser()

    def tearDown(self):
        self.shortInput.close()

    def test_parseLine(self):
        text = self.shortText.split('\n')
        line0 = self.parser.parseLine(text[0])

        self.assertEqual(line0, (0, ['RCiWN dla 2814042 Dywity']))
        line3 = self.parser.parseLine(text[2])
        self.assertEqual(line3, (0, ['Dokument','OA-810/2014 z dnia 2014.06.25']))

    def test_feed_short(self):
        self.parser.feed(self.shortInput)
        docs = self.parser.documents

        # print docs

        self.assertEqual(self.parser.header, 'RCiWN dla 2814042 Dywity')
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['Dokument'], 'OA-810/2014 z dnia 2014.06.25')
        self.assertEqual(len(docs[0][self.parser.SUBDOCUMENT_KEY][0]), 7)
        self.assertEqual(docs[0][self.parser.SUBDOCUMENT_KEY][0]['Dzia�ki'][0]['adres(y)'], 'BUKWA�D 58')

    def test_entity(self):
        self.parser.feed(open(entityTestFile).read())
        docs = self.parser.documents

        self.parser.printDocument(docs, enumerate=True)

    def test_feed_long(self):
        with open(longTestFile) as longInput:
            self.parser.feed(longInput)
        docs = self.parser.documents
        self.parser.printDocument(docs, enumerate=True)
        # for doc in docs:
        #     self.parser.printDocument(doc, enumerate=True)




if __name__ == '__main__':
    unittest.main()