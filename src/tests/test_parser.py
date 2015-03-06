__author__ = 'Adam Kosiorek'
# −*− coding: UTF−8 −*−

import parser

import unittest
import os
import types
import re

projectDataFolder = os.path.join(os.path.join(os.getcwd(), os.pardir), os.pardir)
projectDataFolder = os.path.join(projectDataFolder, 'data/')
shortTestFile = os.path.join(projectDataFolder, 'test.txt')
longTestFile = os.path.join(projectDataFolder, 'gm.txt')
entityTestFile = os.path.join(projectDataFolder, 'entity_test.txt')
commentTestFile = os.path.join(projectDataFolder, 'comment_test.txt')
multipleSubdocTestFile = os.path.join(projectDataFolder, 'multiple_subdoc_test.txt')

class GetParserTest(unittest.TestCase):

    def testBaseParser(self):
        self.assertEqual(type(parser.getParser('base')), parser.BaseParser)

    def testSpaceParser(self):
        self.assertEqual(type(parser.getParser('space')), parser.SpaceParser)

    def testInvalidParserNameRaises(self):
        self.assertRaises(parser.NoSuchParserException, parser.getParser, '')



class BaseParserBasicTest(unittest.TestCase):

    def setUp(self):
        self.shortInput = open(shortTestFile)
        self.shortText = open(shortTestFile).read()
        self.parser = parser.BaseParser(inputEncoding='WINDOWS-1250', outputEncoding='utf-8')

    def tearDown(self):
        self.shortInput.close()

    def testTakeFile(self):
        '''Parser should parse file-like objects'''
        self.parser.feed(self.shortInput)
        self.assertEqual(len(self.parser.pieces), 33)
        self.assertEqual(len(self.parser.output()), 33)

    def testTakeString(self):
        '''Parser should parse strings'''
        self.parser.feed(self.shortText)
        self.assertEqual(len(self.parser.pieces), 33)
        self.assertEqual(len(self.parser.output()), 33)

    def testRaiseEmptyString(self):
        '''Raise an exception when an empty string passed to feed'''
        self.assertRaises(parser.InvalidInputException, self.parser.feed, '')

    def testRaiseNotStringOrFileInput(self):
        '''Raise an exception when feed given no string nor file-like object'''
        self.assertRaises(parser.InvalidInputException, self.parser.feed, {})

    def testParseSingleLine(self):
        '''Generic parseLine function should put line length as a tag and the rest (w/o) whitespaces as content'''
        expectedTags = [len(line) for line in self.shortText]
        parsedLines = [self.parser.parseLine(line) for line in self.shortText]
        for (line, tag, content) in zip(parsedLines, expectedTags, self.shortText):
            self.assertEqual(line[0], tag)
            self.assertEqual(line[1], content.strip())

    # def testEncoding(self):
    #     '''How do you do that?'''
    #     self.assertTrue(False)

    def testFullOutputOnClose(self):
        '''Return output at any given time; accept additional input'''
        lines = self.shortText.split('\n')
        self.assertEqual(len(self.parser.output()), 0)
        self.parser.feed('\n'.join(lines[:10]))
        self.assertEqual(len(self.parser.output()), 8)
        self.parser.feed('\n'.join(lines[10:]))
        # self.parser.close()
        self.assertEqual(len(self.parser.output()), 33)

    def testTrackLineNumbers(self):
        '''Track the number of currently processed line'''
        lines = self.shortText.split('\n')
        chunks = ((0, 2), (2, 5), (5, 35))
        lastLines = (2, 5, 35)
        chunks = ('\n'.join(lines[chunk[0]:chunk[1]]) for chunk in chunks)
        self.assertEqual(self.parser.line, 0)
        for chunk, lastLineNumber in zip(chunks, lastLines):
            self.parser.feed(chunk)
            self.assertEqual(self.parser.line, lastLineNumber)

    def testTrackCurrentAndLastTags(self):
        '''Track currently processed and previous tags'''
        lines = self.shortText.split('\n')
        chunks = ((0, 2), (2, 5), (5, 34))
        lastTags = ((24, 0), (26, 27), (40, 35))
        chunks = ('\n'.join(lines[chunk[0]:chunk[1]]) for chunk in chunks)
        self.assertEqual(self.parser.line, 0)
        for chunk, (lastTag, currentTag) in zip(chunks, lastTags):
            self.parser.feed(chunk)
            self.assertEqual(self.parser.lastTag, lastTag)
            self.assertEqual(self.parser.currentTag, currentTag)

class BaseParserTagHandlerTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.BaseParser(inputEncoding='WINDOWS-1250', outputEncoding='utf-8')

    def testHandlEmptyLine(self):
        '''Call do_EmptyLine when an empty line is encountered'''
        data = 'a\n\na'
        emptyLineCalled = 0
        def do_EmptyLine(self): self.emptyLineCalled += 1
        self.parser.do_EmptyLine = types.MethodType(do_EmptyLine, self.parser)
        self.parser.emptyLineCalled = 0
        self.assertEqual(self.parser.emptyLineCalled, 0)
        self.parser.feed(data)
        self.assertEqual(self.parser.emptyLineCalled, 1)

    def testNumberedHandlers(self):
        data = 'a\naa\naaa'
        def do_1(self, value): self.called1 += 1
        def do_2(self, value): self.called2 += 1
        def do_3(self, value): self.called3 += 1
        self.parser.do_1 = types.MethodType(do_1, self.parser)
        self.parser.do_2 = types.MethodType(do_2, self.parser)
        self.parser.do_3 = types.MethodType(do_3, self.parser)
        self.parser.called1 = 0
        self.parser.called2 = 0
        self.parser.called3 = 0
        self.parser.feed(data)
        self.assertEqual(self.parser.called1, 1)
        self.assertEqual(self.parser.called2, 1)
        self.assertEqual(self.parser.called3, 1)

class SpaceParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = parser.SpaceParser(inputEncoding='WINDOWS-1250', outputEncoding='utf-8')
        self.SUBDOC_KEY = self.parser.SUBDOCUMENT_KEY

    def processFile(self, file):
        data = open(file).read()
        self.parser.feed(data)
        self.output = self.parser.output()

    def testShortInput(self):
        '''Exhaustive test of a short input'''
        self.processFile(shortTestFile)
        docs = self.output
        doc = docs[0]
        subdoc = doc[self.SUBDOC_KEY][0]
        dzialki = subdoc['Dzia�ki'.decode('WINDOWS-1250')]
        budynki = subdoc['Budynki']

        self.assertEqual(self.parser.header, 'RCiWN dla 2814042 Dywity')
        self.assertEqual(len(docs), 1)
        self.assertEqual(len(doc), 8)
        self.assertEqual(len(subdoc), 7)
        self.assertEqual(len(dzialki), 1)
        self.assertEqual(len(budynki), 2)
        self.assertEqual(len(dzialki[0]), 5)
        self.assertEqual(len(budynki[0]), 6)
        self.assertEqual(len(budynki[1]), 6)

    def testMultipleSameEntitiesTest(self):
        '''Exhaustive test of a short input file with multiple entity types'''
        self.processFile(entityTestFile)
        docs = self.output
        doc = docs[0]
        subdoc = doc[self.SUBDOC_KEY][0]
        dzialki = subdoc['Dzia�ki'.decode('WINDOWS-1250')]
        budynki = subdoc['Budynki']
        lokale = subdoc['Lokale']
        lokalePomieszczenia = lokale[0]['Pomieszczenia przynale�ne'.decode('WINDOWS-1250')]

        self.assertEqual(self.parser.header, 'RCiWN dla 2814042 Dywity')
        self.assertEqual(len(docs), 1)
        self.assertEqual(len(doc), 8)
        self.assertEqual(len(subdoc), 8)
        self.assertEqual(len(dzialki), 1)
        self.assertEqual(len(budynki), 1)
        self.assertEqual(len(dzialki[0]), 5)
        self.assertEqual(len(budynki[0]), 6)
        self.assertEqual(len(lokale[0]), 8)
        self.assertEqual(len(lokalePomieszczenia), 2)

    def testMultipleSubdocuments(self):
        self.processFile(multipleSubdocTestFile)
        docs = self.output
        doc = docs[0]
        subdocs = doc[self.SUBDOC_KEY]
        self.assertEqual(len(subdocs), 2)
        self.assertEqual(len(subdocs[0]), 6)
        self.assertEqual(len(subdocs[1]), 5)

    def testLongComments(self):
        '''Multiline comments should be concatenated into a one long comment'''
        self.processFile(commentTestFile)
        docs = self.output

        expectedResults = ('''345000 W TYM PODATEK VAT NA DZIA�CE ZNAJDUJE SI�
                                WOLNOSTOJ�CY ,NIEPODPIWNICZONY,PARTEROWY Z
                                PODDASZEM U�YTKOWYM BUDYNEK MIESZKALNY O POW. U�
                                150,70 M.KW W STANIE SUROWYM ZAMKNI�TYM''',
                                'grunty orne -R',

                                '''S�u�ebno�� gruntowa
                                S�U�EBNO�� GRUNTOWA POLEGAJ�CA NA PRAWIE PRZEJ�CIA
                                I PRZEJAZDU PRZEZ DZ. 97/46 ORAZ NA PRAWIE
                                PRZEPROWADZENIA PRZEZ TEREN DZ. 97/46 INST.
                                WODOCI�GOWEJ, KANALIZ.,ELEKTRYCZ, GAZOWEJ, TELEFON
                                DO DROGI PUBLICZNEJ''',
                                '11 - Myki')

        expectedResults = [re.sub(r'\s+', ' ', result).decode('WINDOWS-1250') for result in expectedResults]

        comments = (docs[0][self.SUBDOC_KEY][0]['Opis'],
                    docs[0][self.SUBDOC_KEY][0]['Rodzaj u�ytku'.decode('WINDOWS-1250')],
                    docs[1][self.SUBDOC_KEY][0]['Obci��enia'.decode('WINDOWS-1250')],
                    docs[1][self.SUBDOC_KEY][0]['Obr�b'.decode('WINDOWS-1250')])

        for (comment, result) in zip(comments, expectedResults):
            self.assertEqual(comment, result)

    def testRegression(self):
        with open(longTestFile) as input:
            self.parser.feed(input)
        self.parser.printDocument(self.parser.output())


if __name__ == '__main__':
    unittest.main()