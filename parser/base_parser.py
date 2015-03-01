__author__ = 'Adam Kosiorek'
# −*− coding: UTF−8 −*−

import types

DEBUG = False

class UnknownTagException(Exception): pass

class BaseParser(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.lastTag = None
        self.currentTag = None
        self.pieces = []
        self.line = 0

    def handleUnknownTag(self, tag, value):
        if value == ['']:
            self.do_EmptyLine()
        else:
            raise UnknownTagException('Unknown tag: %s=%s at %d. line' % (str(tag), str(value), self.line))

    def handleTag(self, tag, value):
        self.line += 1
        if tag != self.currentTag:
            self.lastTag = self.currentTag
            self.currentTag = tag
        self.debug((tag, value))
        try:
            getattr(self, 'do_' + str(tag))(value)
        except AttributeError:
            self.handleUnknownTag(tag, value)

    def __prepare_string_input(self, text):
        from StringIO import StringIO
        textInput = StringIO(text)
        self.feed(textInput)

    def feed(self, input):
        if type(input) == types.StringType:
            input = self.__prepare_string_input(input)
        self.__process(input)

    def __process(self, input):
        lines = [self.parseLine(line) for line in input.read().split('\n')]
        for tag, value in lines:
            self.handleTag(tag, value)

    def parseLine(self, line):
        parsed = str(line).split(':', 1)
        if len(parsed) == 1: parsed.insert(0, 'tag')
        return tuple(parsed)

    def debug(self, text=''):
        if DEBUG: print self.line,': ', text

    def do_EmptyLine(self):
        pass





import unittest
import os

class BaseParserTest(unittest.TestCase):

    def setUp(self):
        path = os.path.join(os.path.join(os.getcwd(), os.pardir), 'data/test.txt')
        self.input = open(path)
        self.text = open(path).read()
        self.parser = BaseParser()

    def tearDown(self):
        self.input.close()

    def test_parseLine(self):
        text = self.text.split('\n')
        line0 = self.parser.parseLine(text[0])
        self.assertEqual(line0, ('tag', 'RCiWN dla 2814042 Dywity'))
        line3 = self.parser.parseLine(text[2])
        self.assertEqual(line3, ('Dokument             ','OA-810/2014 z dnia 2014.06.25'))

    def test_feedString(self):
        self.parser.feedString(self.text)
        stringPieces = list(self.parser.pieces)
        self.parser.reset()
        self.parser.feed(self.input)
        inputPieces = list(self.parser.pieces)
        self.assertEqual(stringPieces, inputPieces)


    def test_feed(self):
        self.parser.feed(self.input)
        pieces = self.parser.pieces

        self.assertEqual(pieces[0], ('tag', 'RCiWN dla 2814042 Dywity'))
        self.assertEqual(pieces[1], ('tag', ''))
        self.assertEqual(pieces[2], ('Dokument             ','OA-810/2014 z dnia 2014.06.25'))
        self.assertEqual(pieces[-1], ('         adres(y)              ','BUKWA�D 58'))




if __name__ == '__main__':
    unittest.main()
    # import sys
    # suite = eval(sys.argv[1])  # Be careful with this line!
    # unittest.TextTestRunner().run(suite)