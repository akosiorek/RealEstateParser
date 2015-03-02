__author__ = 'Adam Kosiorek'
# −*− coding: UTF−8 −*−

import types

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

    def printDocument(self, doc, indent='\t'):
        for k, v in doc.items():
            if type(v) == dict:
                print '%s%s:' %(indent, k)
                self.printDocument(v, indent + '\t')
            elif type(v) == list:
                print '%s%s:' %(indent, k)
                indent += '\t'
                for entry in v:
                    self.printDocument(entry, indent)
            else:
                print '%s%s:%s' %(indent, k, v)

if __name__ == '__main__':
    print 'aha'
    print getParser('base')
    print getParser('space')
    print getParser('')