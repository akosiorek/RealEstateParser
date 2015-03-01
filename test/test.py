import unittest
from base_parser.classes import *

class DocumentTest(unittest.TestCase):

    def testIsEmpty(self):
        doc = Document()
        self.failIf(doc.content)
        self.failIf(doc.parts)

    def testRecentDoc(self):
        doc = Document()
        self.failIf(doc.recent_doc())

        doc.parts.append(Document())
        self.failUnless(doc.recent_doc())

    def testRecentEstate(self):
        doc = Document()
        self.failIf(doc.recent_estate())

        doc.parts.append(Document())
        self.failIf(doc.recent_estate())

        doc.recent_doc().parts.append(Document())
        self.failUnless(doc.recent_estate())

    def testRecentObj(self):
        doc = Document()
        self.failIf(doc.recent_obj())

        doc.parts.append(Document())
        self.failIf(doc.recent_obj())

        doc.recent_doc().parts.append(Document())
        self.failIf(doc.recent_obj())

        doc.recent_estate().parts.append(Document())
        self.failUnless(doc.recent_obj())

    def testLowLevelCount(self):
        doc = Document()
        self.failUnlessEqual(doc.low_level_count(), 0)

        doc.parts.append(Document())
        self.failUnlessEqual(doc.low_level_count(), 0)

        doc.recent_doc().parts.append('')
        self.failUnlessEqual(doc.low_level_count(), 1)

        # doc.parts.append('')
        # self.failUnlessEqual(doc.low_level_count(), 2)

class EntityExtractorTest(unittest.TestCase):

    def testExtractEmpty(self):
        extractor = EntityExtractor()
        self.failIf(extractor.extract([]))
        self.failIf(extractor.extract(['']))

    def testExtractNullKeys(self):
        extractor = EntityExtractor()
        self.assertRaises(KeyError, extractor.extract, [['', '']])

    def testExtractNonRepetition(self):
        extractor = EntityExtractor()
        single_pair = extractor.extract([['key', 'value']])

        self.assertEqual(len(single_pair), 1)
        self.assertEqual(single_pair[0]['key'], 'value')
        self.assertEqual(len(single_pair[0]), 1)

        extractor.clear_key_set()
        double_pair1 = [[1, 11], [2, 22]]
        double_pair1 = extractor.extract(double_pair1)
        self.assertEqual(len(double_pair1), 1)
        self.assertEqual(len(double_pair1[0]), 2)
        self.assertEqual(double_pair1[0][1], 11)
        self.assertEqual(double_pair1[0][2], 22)

    def testKeyExtract(self):
        extractor = EntityExtractor()

        single_data = [[1, 1], [2, 2], [3, 3]]
        self.assertEqual(extractor.extract_keys(single_data), set([1, 2, 3]))

        double_data = [[1, 1], [2, 2], [1, 3], [2, 4], [5, 6]]
        self.assertEqual(extractor.extract_keys(double_data), set([1, 2, 5]))

    def testExtractRepetition(self):
        extractor = EntityExtractor()
        double_pair2 = [[1, 11], [1, 12]]
        double_pair2 = extractor.extract(double_pair2)
        self.assertEqual(len(double_pair2), 2)
        for pair in double_pair2:
            self.assertEqual(len(pair), 1)
        self.assertEqual(double_pair2[0][1], 11)
        self.assertEqual(double_pair2[1][1], 12)

    def testKnownKeyset(self):
        extractor = EntityExtractor(set([1, 2, 3]))

        data = [[1, 2], [3, 4], [3, 5], [5, 6]]
        result = [{1:2, 3:4}, {3:5}]
        self.assertEqual(extractor.extract(data), result)

if __name__ == '__main__':
    unittest.main()
