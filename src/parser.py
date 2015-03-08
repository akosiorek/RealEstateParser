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

class ParseException(Exception): pass
class InvalidInputException(ParseException): pass
class NoSuchParserException(ParseException): pass
class UnknownTagException(ParseException): pass
class UnexpectedParseCaseException(ParseException): pass

class BaseParser(object):
    def __init__(self, inputEncoding=None, outputEncoding=None):
        self.reset(inputEncoding, outputEncoding)

    def reset(self, inputEncoding=None, outputEncoding=None):
        self.lastTag = None
        self.currentTag = None
        self.pieces = []
        self.line = 0
        self.closeFileOnExit = False
        self.inputEncoding = True and inputEncoding or sys.getdefaultencoding()
        self.outputEncoding = True and outputEncoding or sys.getdefaultencoding()

    def handleUnknownTag(self, tag, value):
        if self.isEmptyLine(value):
            self.do_EmptyLine()
        else:
            # raise UnknownTagException('Unknown tag: %s=%s at %d. line' % (str(tag), str(value), self.line))
            self.pieces.append((tag, value))

    def handleTag(self, tag, value):
        try:
            getattr(self, 'do_%s' %(tag))(value)
        except AttributeError:
            self.handleUnknownTag(tag, value)

    def feed(self, input):
        if not hasattr(input, 'read'):
            try:
                if type(input) != str or len(input) == 0:
                    raise InvalidInputException
                input = open(input, 'r')
                self.closeFileOnExit = True
            except (OSError, IOError) as e:
                from StringIO import StringIO
                input = StringIO(input)

        self.__process(input)

    def __process(self, input):
        # TODO come up with a solution that does not require reading the whole file at once!
        data = input.read().split('\n')
        for line in data:
            self.line += 1
            if self.inputEncoding:
                line = self.decode(line)
            tag, value = self.parseLine(line)
            if tag != self.currentTag:
                self.lastTag, self.currentTag = self.currentTag, tag
            self.debug((tag, value))
            self.handleTag(tag, value)

        if self.closeFileOnExit:
            input.close()
            self.closeFileOnExit = False

    def parseLine(self, line):
        '''Parse a single line'''
        return (len(line), line.strip())

    def isEmptyLine(self, value):
        return value == ''

    def output(self):
        return [(tag, self.encode(content)) for (tag, content) in self.pieces]

    def decode(self, str):
        return str.decode(self.inputEncoding)

    def encode(self, str):
        return str.encode(self.outputEncoding)

    def debug(self, text=''):
        if DEBUG: print self.line,':', text

    def do_EmptyLine(self):
        pass


# TODO: add level-wise keyword discovery
class SpaceParser(BaseParser):
    DOCUMENT_END = '======================================================================'
    SUBDOCUMENT_END = '----------------------------------------------------------------------'
    EMPTY_LINE = ''
    SUBDOCUMENT_KEY = 'SUBDOCUMENT'
    LONGEST_KEY = 20

    def __self__(self, inputEncoding=None, outputEncoding=None):
        BaseParser.__init__(self, inputEncoding, outputEncoding)

    def reset(self, inputEncoding=None, outputEncoding=None):
        self.currentDocument = None
        self.currentSubdocument = None
        self.currentEntity = None
        self.header = None
        self.current0 = None
        self.current5 = None
        self.current9 = None
        self.keys = {}
        BaseParser.reset(self, inputEncoding, outputEncoding)

    def handleTag(self, tag, value):
        BaseParser.handleTag(self, tag, value)

        # save unique keys for each tag
        if not tag in self.keys:
            self.keys[tag] = set()
        if tag < self.LONGEST_KEY:
            self.keys[tag].add(value[0])

    def parseLine(self, line):
        tag = len(line) - len(line.lstrip())
        line = [part.strip() for part in line.split(':')]
        return (tag, line)

    def isEmptyLine(self, value):
        return len(value) == 0 or len(value) == 1 and value[0] == ''

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

    def do_31(self, value):
        self.currentTag = 32
        self.do_32(value)

    def do_32(self, value):

        if self.lastTag == 5:
            self.currentSubdocument[self.current5] += ' ' + ' '.join(value).strip()
        elif self.lastTag == 9:
            self.currentEntity[self.current9] += ' ' + ' '.join(value).strip()
        else:
            # print self.lastTag, self.line
            raise UnexpectedParseCaseException

    def do_EmptyLine(self):
        if self.currentDocument is None:
            self.currentDocument = {}
        else:
            self.currentDocument[self.SUBDOCUMENT_KEY] = []

    def do_DocumentEnd(self):
        if self.currentDocument:
            self.do_SubdocumentEnd()
            self.pieces.append(self.currentDocument)
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

    def output(self, encode=False):
        if encode:
            return self.mapEntries(self.pieces, self.encode, self.encode)
        return self.pieces

    def globalKeyset(self):
        keyset = set()
        for localKeyset in self.keys.values():
            keyset = keyset.union(localKeyset)

        for key in (self.header, self.DOCUMENT_END, self.EMPTY_LINE, self.SUBDOCUMENT_END):
            keyset.remove(key)
        return keyset

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
                    self.printDocument(v, indent + '\t', enumerate)
                else:
                    print '%s%s:%s' %(indent, self.encode(k), self.encode(v))


    def mapEntries(self, elem, keyMapper=lambda x:x, valueMapper=lambda x:x):
        if type(elem) in (list, tuple):
            return [self.mapEntries(entry, keyMapper, valueMapper) for entry in elem]

        d = {}
        for k, v in elem.items():
            k = keyMapper(k)
            if type(v) == dict:
                d[k] = self.mapEntries(v, keyMapper, valueMapper)
            elif type(v) == list:
                d[k] = self.mapEntries(v, keyMapper, valueMapper)
            else:
                d[k] = valueMapper(v)
        return d


if __name__ == '__main__':
    parser = SpaceParser(inputEncoding='WINDOWS-1250', outputEncoding='utf-8')
    parser.feed(open(sys.argv[1]).read())
    # parser.printDocument(parser.output())
    for key in parser.globalKeyset():
        print key