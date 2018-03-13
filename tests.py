#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Tests for data conversion
"""
import datetime
import io
from collections import defaultdict
import unittest
from pprint import pprint

from approvaltests.Approvals import verify
from rdflib import Graph, RDF, URIRef
from rdflib import Literal
from rdflib import XSD
from rdflib.compare import isomorphic, graph_diff

import converters
from csv_to_rdf import RDFMapper
from mapping import PRISONER_MAPPING, DATA_NS, DC


class TestConverters(unittest.TestCase):

    def test_convert_int(self):
        self.assertIsInstance(converters.convert_int('1234'), int)

        self.assertEqual(converters.convert_int('5'), 5)
        self.assertEqual(converters.convert_int('0'), 0)
        self.assertEqual(converters.convert_int('-5'), -5)

        self.assertEqual(converters.convert_int(''), '')
        self.assertEqual(converters.convert_int('foobar'), 'foobar')

    def test_convert_dates(self):
        self.assertEqual(converters.convert_dates('24.12.2016'), datetime.date(2016, 12, 24))
        self.assertEqual(converters.convert_dates('24/12/2016'), datetime.date(2016, 12, 24))

        self.assertEqual(converters.convert_dates('xx.xx.xxxx'), 'xx.xx.xxxx')
        self.assertEqual(converters.convert_dates('xx.09.2016'), 'xx.09.2016')

    def test_convert_person_name(self):
        self.assertEqual(converters.convert_person_name('Virtanen Matti Akseli'),
                         ('Matti Akseli', 'Virtanen', 'Virtanen, Matti Akseli'))

        self.assertEqual(converters.convert_person_name('Huurre ent. Hildén Aapo Antero'),
                         ('Aapo Antero', 'Huurre (ent. Hildén)', 'Huurre (ent. Hildén), Aapo Antero'))

        self.assertEqual(converters.convert_person_name('Kulento ent. Kulakov Nikolai (Niilo)'),
                         ('Nikolai (Niilo)', 'Kulento (ent. Kulakov)', 'Kulento (ent. Kulakov), Nikolai (Niilo)'))

        self.assertEqual(converters.convert_person_name('Ahjo ent. Germanoff Juho ent. Ivan'),
                         ('Juho Ent. Ivan', 'Ahjo (ent. Germanoff)', 'Ahjo (ent. Germanoff), Juho Ent. Ivan'))

    def test_strip_dash(self):
        assert not converters.strip_dash('-')
        assert converters.strip_dash('Foo-Bar') == 'Foo-Bar'


class TestRDFMapper(unittest.TestCase):

    def test_read_value_with_source(self):
        mapper = RDFMapper({}, '')

        assert mapper.read_value_with_source('Some text') == ('Some text', [])
        assert mapper.read_value_with_source('Some text (source A)') == ('Some text', ['source A'])
        assert mapper.read_value_with_source('Some text (source A, source B)') == ('Some text',
                                                                                   ['source A', 'source B'])

    def test_read_semicolon_separated(self):
        mapper = RDFMapper({}, '')

        assert mapper.read_semicolon_separated('Some text') == ('Some text', [], None, None)
        assert mapper.read_semicolon_separated('Source: Value') == ('Value', ['Source'], None, None)
        assert mapper.read_semicolon_separated('Source1, Source2: Value') == ('Value', ['Source1', 'Source2'], None, None)
        assert mapper.read_semicolon_separated('http://example.com/') == ('http://example.com/', [], None, None)

        assert mapper.read_semicolon_separated('54 13.10.1997-xx.11.1997') == ('54', [], datetime.date(1997, 10, 13), 'xx.11.1997')

    def test_read_csv_simple(self):
        test_csv = '''col1  col2    col3
        1   2   3
        4   5   6
        7   8   9
        '''

        mapper = RDFMapper({}, '')
        mapper.read_csv(io.StringIO(test_csv))
        assert len(mapper.table) == 3

    def test_read_csv_simple_2(self):
        mapper = RDFMapper({}, '')
        mapper.read_csv('test_data.csv')
        assert len(mapper.table) == 2

    def test_mapping_field_contents(self):
        instance_class = URIRef('http://example.com/Class')

        mapper = RDFMapper(PRISONER_MAPPING, instance_class)
        mapper.read_csv('test_data.csv')
        mapper.process_rows()
        rdf_data, schema = mapper.serialize(None, None)
        g = Graph().parse(io.StringIO(rdf_data.decode("utf-8")), format='turtle')

        # g.serialize('test_data.ttl', format="turtle")  # Decomment to update file, and verify it by hand
        g2 = Graph().parse('test_data.ttl', format='turtle')

        diffs = graph_diff(g, g2)

        print('In new:')
        pprint([d for d in diffs[1]])

        print('In old:')
        pprint([d for d in diffs[2]])

        assert isomorphic(g, g2)  # Isomorphic graph comparison

if __name__ == '__main__':
    unittest.main()
