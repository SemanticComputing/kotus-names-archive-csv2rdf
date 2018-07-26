#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Convert from CSV to RDF.
"""

import argparse
import logging
import pandas as pd
from rdflib import URIRef, Graph, Literal
from mapping import KOTUS_MAPPING
from namespaces import *
import csv
from pathlib import Path
from finnsyll import FinnSyll
f = FinnSyll()

class RDFMapper:
    """
    Map tabular data (currently pandas DataFrame) to RDF. Create a class instance of each row.
    """

    def __init__(self, mapping, instance_class, loglevel='WARNING'):
        self.mapping = mapping
        self.instance_class = instance_class
        self.table = None
        self.data = Graph()
        self.schema = Graph()
        logging.basicConfig(filename='kotus.log',
                            filemode='a',
                            level=getattr(logging, loglevel),
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        self.log = logging.getLogger(__name__)

    def map_row_to_rdf(self, row):
        """
        Map a single row to RDF.

        :param row: tabular data
        :return:
        """
        row_rdf = Graph()

        # URI of the instance being created
        entity_uri = DATA_NS[str(row['RerSer'])]

        # Loop through the mapping dict and convert the row to RDF
        for column_name in self.mapping:

            mapping = self.mapping[column_name]
            value = row[column_name]
            converter = mapping.get('converter')
            value = converter(value) if converter else value

            liter = None

            if column_name == 'Vuosi' and value != '':
                liter = Literal(value, datatype=XSD.int)
            elif column_name == 'wgs84_lat':
                if value is not None:
                    liter = Literal(value, datatype=XSD.float)
            elif column_name == 'wgs84_long':
                if value is not None:
                    liter = Literal(value, datatype=XSD.float)
            elif column_name == 'Paikanlaji':
                liter = Literal(value, lang='fi')
            else:
                liter = Literal(value)

            if liter:
                row_rdf.add((entity_uri, mapping['uri'], liter))

            # Use FinnSyll to split place name into modifier and basic element if possible
            if column_name == 'Paikannimi':
                splitted = f.split(value)
                if '=' in splitted:
                    lastIndex = splitted.rindex('=')+1
                    modifier = splitted[:lastIndex].replace('=', '')  # määriteosa
                    basic_element = splitted[lastIndex:] # perusosa
                    row_rdf.add((entity_uri, SCHEMA_NS['place_name_modifier'], Literal(modifier, lang='fi')))
                    row_rdf.add((entity_uri, SCHEMA_NS['place_name_basic_element'], Literal(basic_element, lang='fi')))

            if row_rdf:
                row_rdf.add((entity_uri, RDF.type, self.instance_class))
            else:
                # Don't create class instance if there is no data about it
                self.log.warning('No data found for {uri}'.format(uri=entity_uri))

        return row_rdf


    def read_csv(self, csv_input):
        """
        Read in a CSV files using pandas.read_csv

        :param csv_input: CSV input (filename or buffer)
        """
        csv_data = pd.read_csv(csv_input, encoding='UTF-8', sep=',', na_values=[''])

        self.table = csv_data.fillna('').applymap(lambda x: x.strip() if type(x) == str else x)
        self.log.info('Data read from CSV %s' % csv_input)


    def serialize(self, destination_data, destination_schema):
        """
        Serialize RDF graphs

        :param destination_data: serialization destination for data
        :param destination_photographs: serialization destination for photo data
        :param destination_schema: serialization destination for schema
        :return: output from rdflib.Graph.serialize
        """
        bind_namespaces(self.data)

        data = self.data.serialize(format="turtle", destination=destination_data)
        schema = self.schema.serialize(format="turtle", destination=destination_schema)

        self.log.info('Data serialized to %s' % destination_data)
        self.log.info('Schema serialized to %s' % destination_schema)

        return data, schema  # Return for testing purposes

    def process_rows(self):
        """
        Loop through CSV rows and convert them to RDF
        """

        for index in range(len(self.table)):
            row_rdf = self.map_row_to_rdf(self.table.ix[index])
            if row_rdf:
                self.data += row_rdf

        # generate schema RDF
        for prop in KOTUS_MAPPING.values():

            if 'uri' in prop:
                self.schema.add((prop['uri'], RDF.type, RDF.Property))
                if 'name_fi' in prop:
                    self.schema.add((prop['uri'], SKOS.prefLabel, Literal(prop['name_fi'], lang='fi')))
                if 'name_en' in prop:
                    self.schema.add((prop['uri'], SKOS.prefLabel, Literal(prop['name_en'], lang='en')))
            else:
                continue

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Process cemeteries CSV", fromfile_prefix_chars='@')

    argparser.add_argument("input", help="Input CSV file")
    argparser.add_argument("output", help="Output location to serialize RDF files to")
    argparser.add_argument("mode", help="CSV conversion mode", default="KOTUS", choices=["KOTUS"])
    argparser.add_argument("--loglevel", default='INFO', help="Logging level, default is INFO.",
                           choices=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

    args = argparser.parse_args()

    output_dir = args.output + '/' if args.output[-1] != '/' else args.output

    if args.mode == "KOTUS":
        mapper = RDFMapper(KOTUS_MAPPING, SCHEMA_NS['Place'], loglevel=args.loglevel.upper())
        mapper.read_csv(args.input)
        mapper.process_rows()
        mapper.serialize(output_dir + "names-archive.ttl", output_dir + "schema.ttl")
