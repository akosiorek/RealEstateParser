import unittest

from base_parser.classes import DocumentBuilder


class DocumentBuilderTest(unittest.TestCase):

    def testGetLinesOneline(self):
        builder = DocumentBuilder('\n')
        text = 'text'
        self.assertEqual(builder.get_lines(text), ['text'])


    def testGetLinesMoreLines(self):
        builder = DocumentBuilder('\n')
        text = 'aha\nwhat now?\nnothing'

        self.assertEqual(len(builder.get_lines(text)), 3)
        self.assertEqual(builder.get_lines(text), ['aha', 'what now?', 'nothing'])

    def testExtractHeader(self):
        builder = DocumentBuilder('\n')

        text = 'header\n\nrest\nsomething\nelse'

        self.assertEqual(builder.extract_header(text)[0], 'header')
        self.assertEqual(builder.extract_header(text)[1], '\nrest\nsomething\nelse')

    def testExtractParts1(self):
        builder = DocumentBuilder('\n', ('HIGH',))

        text = ' document1\nHIGH\ndocument2\nHIGH\ndocument3\n'
        self.assertEqual(builder.extract_parts(text), [[' document1'], ['document2'], ['document3']])

    def testExtractParts21(self):
        builder = DocumentBuilder('\n', ('HIGH', 'MEDIUM'))

        text = 'high1\n' \
               'MEDIUM\n' \
               'medium11\n' \

        result = [
            ['high1',
             ['medium11',]
            ],
        ]

        self.assertEqual(builder.extract_parts(text), result)

    def testExtractParts22(self):
        builder = DocumentBuilder('\n', ('HIGH', 'MEDIUM'))

        text = 'high1\n' \
                   'MEDIUM\n' \
                   'medium11\n' \
                   'MEDIUM\n' \
                   'medium12\n' \
               'HIGH\n' \
               'high2\n' \
                   'MEDIUM\n' \
                   'medium21\n' \
               'HIGH\n' \
               'high3\n'

        result = [
            ['high1',
                ['medium11'],
                ['medium12']
            ],
            ['high2',
                ['medium21']
            ],
            ['high3']
        ]

        self.assertEqual(builder.extract_parts(text), result)

    def testExtractParts31(self):
        builder = DocumentBuilder('\n', ('HIGH', 'MEDIUM', 'LOW'))

        text = 'high1\n' \
                   'MEDIUM\n' \
                   'medium11\n' \
                       'LOW\n' \
                       'low111' \
                   'MEDIUM\n' \
                   'medium12\n' \
               'HIGH\n' \
               'high2\n' \
                   'MEDIUM\n' \
                   'medium21\n' \
               'HIGH\n' \
               'high3\n'

        result = [
            ['high1',
             ['medium11',
                ['low111']
             ],
             ['medium12']
            ],
            ['high2',
             ['medium21']
            ],
            ['high3']
        ]

        self.assertEqual(builder.extract_parts(text), result)

    def testExtractParts32(self):
        builder = DocumentBuilder('\n', ('HIGH', 'MEDIUM', 'LOW'))

        text = 'high1\n' \
                    'MEDIUM\n' \
                    'medium11\n' \
                        'LOW\n' \
                       'low111\n' \
                       'LOW\n' \
                       'low112\n' \
                   'MEDIUM\n' \
                   'medium12\n' \
                       'LOW\n' \
                       'low121' \
               'HIGH\n' \
               'high2\n' \
                   'MEDIUM\n' \
                   'medium21\n' \
               'HIGH\n' \
               'high3\n' \
                   'MEDIUM\n' \
                   'medium31' \
                       'LOW\n' \
                       'low311'

        result = [
                ['high1',
                    ['medium11',
                        ['low111'],
                        ['low112']
                    ],
                    ['medium12',
                        ['low121']
                    ]
                ],
                ['high2',
                    ['medium21']
                ],
                ['high3',
                    ['medium31',
                        ['low311']
                    ]
                ]
            ]

        self.assertEqual(builder.extract_parts(text), result)

    def testExtractParts1MultipleSeps(self):
        builder = DocumentBuilder('\n', (('HIGH', '!high!'),))

        text = ' document1\nHIGH\ndocument2\n!high!\ndocument3\n'
        self.assertEqual(builder.extract_parts(text), [[' document1'], ['document2'], ['document3']])

    def testExtractParts3MultipleSeps(self):
        builder = DocumentBuilder('\n', (('HIGH', '!high!'), ('MEDIUM', '!medium!'), ('LOW', '@low@')))

        text = 'high1\n' \
                   'MEDIUM\n' \
                   'medium11\n' \
                       'LOW\n' \
                       'low111\n' \
                       'LOW\n' \
                       'low112\n' \
                   'MEDIUM\n' \
                   'medium12\n' \
                       'LOW\n' \
                       'low121' \
               'HIGH\n' \
               'high2\n' \
                   'MEDIUM\n' \
                   'medium21\n' \
               'HIGH\n' \
               'high3\n' \
                   'MEDIUM\n' \
                   'medium31' \
                       'LOW\n' \
                       'low311'

        result = [
            ['high1',
             ['medium11',
              ['low111'],
              ['low112']
             ],
             ['medium12',
              ['low121']
             ]
            ],
            ['high2',
             ['medium21']
            ],
            ['high3',
             ['medium31',
              ['low311']
             ]
            ]
        ]

        self.assertEqual(builder.extract_parts(text), result)



