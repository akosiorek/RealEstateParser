__author__ = 'Adam Kosiorek'
# −*− coding: UTF−8 −*−

import types
import sys

DEBUG = False


def getParser(name):
    name = '%sParser' % (name.capitalize())
    parserClass = None
    try:
        parserClass = globals()[name]
    except KeyError:
        raise NoSuchParserException
    return parserClass()

class NoSuchParserException(Exception): pass
class UnknownTagException(Exception): pass

class BaseParser(object):
    def __init__(self, inputEncoding=None, outputEncoding=None):
        self.reset(inputEncoding, outputEncoding)

    def reset(self, inputEncoding=None, outputEncoding=None):
        self.lastTag = None
        self.currentTag = None
        self.pieces = []
        self.line = 0
        self.inputEncoding = True and inputEncoding or sys.getdefaultencoding()
        self.outputEncoding = True and outputEncoding or sys.getdefaultencoding()

    def handleUnknownTag(self, tag, value):
        if value == ['']:
            self.do_EmptyLine()
        else:
            # raise UnknownTagException('Unknown tag: %s=%s at %d. line' % (str(tag), str(value), self.line))
            self.pieces.append((tag, value))

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
        return StringIO(text)

    def feed(self, input):
        if type(input) == types.StringType:
            input = self.__prepare_string_input(input)
        self.__process(input)

    def __process(self, input):
        data = input.read()
        if self.inputEncoding:
            data = self.decode(data)

        lines = [self.parseLine(line) for line in data.split('\n')]

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

    def output(self):
        pass

    def decode(self, str):
        return str.decode(self.inputEncoding)

    def encode(self, str):
        return str.encode(self.outputEncoding)


# TODO: add level-wise keyword discovery
class SpaceParser(BaseParser):
    DOCUMENT_END = '======================================================================'
    SUBDOCUMENT_END = '----------------------------------------------------------------------'
    EMPTY_LINE = ''
    SUBDOCUMENT_KEY = 'SUBDOCUMENT'

    def __self__(self, inputEncoding=None, outputEncoding=None):
        BaseParser.__init__(self, inputEncoding, outputEncoding)

    def reset(self, inputEncoding=None, outputEncoding=None):
        self.documents = []
        self.currentDocument = None
        self.currentSubdocument = None
        self.currentEntity = None
        self.header = None
        self.current0 = None
        self.current5 = None
        self.current9 = None
        self.keys = {}
        BaseParser.reset(self, inputEncoding, outputEncoding)

        self.jointLines = 0

    def handleTag(self, tag, value):
        BaseParser.handleTag(self, tag, value)
        if not tag in self.keys:
            self.keys[tag] = set()
        self.keys[tag].add(value[0])

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

        if self.currentEntity:
            self.do_EntityEnd()

        self.current5 = value[0]
        self.currentSubdocument[value[0]] = value[1]

    def do_9(self, value):
        if self.currentSubdocument[self.current5] == '':
            self.do_EntityEnd()
            self.currentSubdocument[self.current5] = []
            # self.currentEntity = {}

        self.current9 = value[0]
        if value[0] in self.currentEntity:
            self.currentSubdocument[self.current5].append(self.currentEntity)
            self.currentEntity = {}

        self.currentEntity[value[0]] = value[1]


    def do_12(self, value):
        if self.currentEntity[self.current9] == '':
            self.currentEntity[self.current9] = {}

        self.currentEntity[self.current9][value[0]] = value[1]


    def do_22(self, value):
        self.currentDocument[self.current0] += ' '.join(value)
        self.jointLines += 1

    def do_31(self, value):
        self.currentTag = 32
        self.do_32(value)

    def do_32(self, value):

        if self.lastTag == 5:
            self.currentSubdocument[self.current5] += ' '.join(value)
            self.jointLines += 1
        elif self.lastTag == 9:
            self.currentEntity[self.current9] += ' '.join(value)
            self.jointLines += 1
        else:
            print self.lastTag, self.line
            raise Exception()

    def do_EmptyLine(self):
        if self.currentDocument is None:
            self.currentDocument = {}
        else:
            self.currentDocument[self.SUBDOCUMENT_KEY] = []

    def do_DocumentEnd(self):
        if self.currentDocument:
            self.do_SubdocumentEnd()
            self.documents.append(self.currentDocument)
        self.currentDocument = {}

    def do_SubdocumentEnd(self):
        if self.currentSubdocument:
            self.do_EntityEnd()
            self.currentDocument[self.SUBDOCUMENT_KEY].append(self.currentSubdocument)
        self.currentSubdocument = {}

    def do_EntityEnd(self):
        if self.currentEntity:
            self.currentSubdocument[self.current5].append(self.currentEntity)
        self.currentEntity = {}


    def printDocument(self, doc, indent='\t', enumerate=False):
        if type(doc) in (list, tuple):
            for (entry, num) in zip(doc, xrange(1, len(doc) + 1)):
                if enumerate: print '%s%d:' %(indent, num)
                self.printDocument(entry, indent, enumerate)

        else:
            for k, v in doc.items():
                if type(v) == dict:
                    print '%s%s:' %(indent, self.encode(k))
                    self.printDocument(v, indent + '\t')
                elif type(v) == list:
                    print '%s%s:' %(indent, self.encode(k))
                    # indent += '\t'
                    # for entry in v:
                    #     self.printDocument(entry, indent)
                    self.printDocument(v, indent + '\t', enumerate)
                else:
                    print '%s%s:%s' %(indent, self.encode(k), self.encode(v))


if __name__ == '__main__':
    parser = SpaceParser(inputEncoding='WINDOWS-1250', outputEncoding='utf-8')
    parser.feed(open(sys.argv[1]).read())
    parser.printDocument(parser.documents)
