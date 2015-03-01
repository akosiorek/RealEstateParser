__author__ = 'Adam Kosiorek'
# −*− coding: UTF−8 −*−

from base_parser import BaseParser


class SpaceParser(BaseParser):
    DOCUMENT_END = '======================================================================'
    SUBDOCUMENT_END = '----------------------------------------------------------------------'
    EMPTY_LINE = ''
    SUBDOCUMENT_KEY = 'SUBDOCUMENT'

    def __self__(self):
        BaseParser.__init__(self)

    def reset(self):
        self.documents = []
        self.currentDocument = None
        self.currentSubdocument = None
        self.header = None
        self.current0 = None
        self.current5 = None
        self.current9 = None
        BaseParser.reset(self)

    def parseLine(self, line):
        tag = len(line) - len(line.lstrip())
        line = [part.strip() for part in line.split(':')]
        return (tag, line)

    def do_0(self, value):
        if not self.header:
            self.header = value[0]
        elif value[0] == self.EMPTY_LINE:
            self.do_EmptyLine()
        elif value[0] == self.DOCUMENT_END:
            self.do_DocumentEnd()
        elif value[0] == self.SUBDOCUMENT_END:
            self.do_SubdocumentEnd()
        elif not self.currentDocument is None:
            self.current0 = value[0]
            self.currentDocument[value[0]] = value[1]

    def do_5(self, value):
        if self.currentSubdocument is None:
            self.currentSubdocument = {}

        self.current5 = value[0]
        # self.currentDocument[self.SUBDOCUMENT_KEY][value[0]] = value[1]
        self.currentSubdocument[value[0]] = value[1]

    def do_9(self, value):
        if self.currentSubdocument[self.current5] == '':
            self.currentSubdocument[self.current5] = {}

        self.current9 = value[0]
        self.currentSubdocument[self.current5][value[0]] = value[1]


    def do_12(self, value):
        if self.currentSubdocument[self.current5][self.current9] == '':
            self.currentSubdocument[self.current5][self.current9] = {}

        self.currentSubdocument[self.current5][self.current9][value[0]] = value[1]


    def do_22(self, value):
        self.currentDocument[self.current0] += ' '.join(value)

    def do_31(self, value):
        self.currentTag = 32
        self.do_32(value)

    def do_32(self, value):

        if self.lastTag == 5:
            self.currentSubdocument[self.current5] += ' '.join(value)
        elif self.lastTag == 9:
            self.currentSubdocument[self.current5][self.current9] += ' '.join(value)
        else:
            print self.lastTag, self.line
            raise Exception()

    def do_EmptyLine(self):
        if self.currentDocument is None:
            self.currentDocument = {}
        else:
            self.currentDocument[self.SUBDOCUMENT_KEY] = []

    def do_DocumentEnd(self):
        self.do_SubdocumentEnd()
        self.documents.append(self.currentDocument)
        self.currentDocument = {}


    def do_SubdocumentEnd(self):
        self.currentDocument[self.SUBDOCUMENT_KEY].append(self.currentSubdocument)
        self.currentSubdocument = {}

def printDocument(doc, indent=0):
    currentIndent = '\t' * indent
    for k, v in doc.items():
        if type(v) == dict:
            print '%s%s:' %(currentIndent, k)
            printDocument(v, indent + 1)
        elif type(v) == list:
            print '%s%s:' %(currentIndent, k)
            for entry in v:
                printDocument(entry, indent + 1)
        else:
            print '%s%s:%s' %(currentIndent, k, v)



import unittest
import os
class SpaceParserTest(unittest.TestCase):

    def setUp(self):
        path = os.path.join(os.path.join(os.getcwd(), os.pardir), 'data/test.txt')
        self.input = open(path)
        self.text = open(path).read()
        self.parser = SpaceParser()

    def tearDown(self):
        self.input.close()

    def test_parseLine(self):
        text = self.text.split('\n')
        line0 = self.parser.parseLine(text[0])

        self.assertEqual(line0, (0, ['RCiWN dla 2814042 Dywity']))
        line3 = self.parser.parseLine(text[2])
        self.assertEqual(line3, (0, ['Dokument','OA-810/2014 z dnia 2014.06.25']))

    def test_feed_short(self):
        self.parser.feed(self.input)
        docs = self.parser.documents

        # print docs

        self.assertEqual(self.parser.header, 'RCiWN dla 2814042 Dywity')
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['Dokument'], 'OA-810/2014 z dnia 2014.06.25')
        self.assertEqual(len(docs[0][self.parser.SUBDOCUMENT_KEY][0]), 7)
        self.assertEqual(docs[0][self.parser.SUBDOCUMENT_KEY][0]['Dzia�ki']['adres(y)'], 'BUKWA�D 58')

    def test_feed_long(self):
        with open('../data/gm.txt') as inputLong:
            self.parser.feed(inputLong)
        docs = self.parser.documents
        for doc in docs:
            printDocument(doc)

if __name__ == '__main__':
    unittest.main()