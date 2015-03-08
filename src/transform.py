__author__ = 'Adam Kosiorek'
# −*− coding: UTF−8 −*−

from parser import SpaceParser
import re
import sys


def getHandlers(name):
    '''Get a list of handlers named "__name.*" sorted in an alphabetical order.
    To ensure priority name the hadlers as:
            "__name1.*" for highest priority and
            "__name9.*" for lowest priority'''

    matcher = re.compile('^__' + name)
    module = sys.modules[__name__]
    handlers = [getattr(module, key) for key in dir(module) if callable(getattr(module, key)) and matcher.match(key)]
    handlers.sort(key=lambda x:x.__name__)
    return handlers

###############################################################################
### Error Handlers  ###########################################################
###############################################################################

def __error_noEstate(doc):
    if u'Nieruchomość' not in doc.keys():
        return False
    return True

def __error_value0(doc):
    try:
        if doc[u'Wartość'] == '0.0':
            return False
    except KeyError:
        return False
    return True

errorMatchers = getHandlers('error')
def hasError(doc):
    for matcher in errorMatchers:
        if not matcher(doc):
            return True
    return False

###############################################################################
### Transformations  ##########################################################
###############################################################################

def aggregateProperties(doc, key, properties):
    properties = {property:[] for property in properties}
    for subdoc in doc[key]:
        for property in properties:
            if property in subdoc.keys():
                properties[property].append(subdoc[property])
                del subdoc[property]
    return properties

buildingKey = u'Budynki'
buildingProperties = {u'adres(y)':u'Adresy budynków', u'Numer':u'Numery budynków'}
def __matchBuilding(doc): return buildingKey in doc.keys()

def __processBuilding(doc):
    # properties = aggregateProperties(doc, buildingKey, buildingProperties.keys())
    # for property, name in buildingProperties.items():
    #     doc[name] = '; '.join(properties[property])
    return doc

estateKey = u'Działki'
estateProperties = {
    u'adres(y)':u'Adresy działek',
    u'Udział w prawie':u'Udziały w prawie',
    u'Numer':u'Numery działek',
    u'Powierzchnia':u'Łączna powierzchnia',
    u'Wartość':u'Łączna wartość działek'
}
def __matchEstate(doc): return estateKey in doc.keys()

def __processEstates(doc):
    properties = aggregateProperties(doc, estateKey, estateProperties.keys())
    print properties
    for property, name in estateProperties.items():
        if properties[property]:
            doc[name] = '; '.join(properties[property])
    return doc

apartmentKey = u'Lokale'
def __matchApartment(doc): return apartmentKey in doc.keys()

def __processApartment(doc):
    #process
    return doc

roadKey = u'Drogi'
def __matchRoad(doc): return roadKey in doc.keys()

def __processRoad(doc):
    #process
    return doc

matchers =  getHandlers('match')
processors = getHandlers('process')
entityProcessors = [(matcher, processor) for matcher, processor in zip(matchers, processors)]

def processEntity(doc):
    for matcher, processor in entityProcessors:
        if matcher(doc):
            doc = processor(doc)
    return doc


estateTypes = ('lokalowa', 'zabudowana', 'niezabudowana', 'droga')
estateMatchers = {k:re.compile(k) for k in estateTypes}

def estateTypeSplit(docs):

    typedEstates = {k:[] for k in estateTypes}
    missed = []
    for doc in docs:
        documentKeyset = doc.keys()
        del documentKeyset[documentKeyset.index(SpaceParser.SUBDOCUMENT_KEY)]
        currentDocument = {k:doc[k] for k in documentKeyset}
        for subdoc in doc[SpaceParser.SUBDOCUMENT_KEY]:
            document = currentDocument.copy()
            document.update(subdoc)
            if hasError(document):
                missed.append(document)
            else:
                estateDescription = document[u'Nieruchomość']

                matched = False
                for estateType, estateMatcher in estateMatchers.items():
                    if estateMatcher.match(estateDescription):
                        typedEstates[estateType].append(processEntity(document))
                        matched = True
                        break
                if not matched:
                    missed.append(document)


    return (typedEstates, missed)



if __name__ == '__main__':
    parser = SpaceParser(inputEncoding='Windows-1250', outputEncoding='utf-8')
    parser.feed('../data/gm.txt')
    # print parser.output()
    typedEstates, missed = estateTypeSplit(parser.output())
    # for k, v in typedEstates.items():
    #     print len(v), k, v

    # print
    # print
    #
    # for miss in missed:
    #     print miss

    for doc in typedEstates['niezabudowana'][:10]:
        print doc

    print getHandlers('error')