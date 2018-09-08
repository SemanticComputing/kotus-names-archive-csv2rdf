#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Convert from CSV to RDF.
"""

import argparse
import logging
import pandas as pd
from rdflib import URIRef, Graph, Literal
from namespaces import *
import csv
from pathlib import Path
from joblib import dump

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
        logging.basicConfig(filename='pnr.log',
                            filemode='a',
                            level=getattr(logging, loglevel),
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        self.latest_theme = None
        self.latest_group = None
        self.latest_subgroup = None
        self.kotus_id = 1
        self.kotus_place_types = {}

    def map_row_to_rdf(self, row):
        """
        Map a single row to RDF.

        :param entity_uri: URI of the instance being created
        :param row: tabular data
        :return:
        """
        row_rdf = Graph()

        super_class = None
        desc = None
        #print(row)

        if row['Paikanlajiteema_id']:
            pnr_id = str(int(row['Paikanlajiteema_id']))
            entity_uri = PNR_SCHEMA_NS['place_type_' + pnr_id]
            label = row['Paikanlajiteema']
            self.latest_theme = entity_uri
        elif row['Paikanlajiryhmä_id']:
            pnr_id = str(int(row['Paikanlajiryhmä_id']))
            entity_uri = PNR_SCHEMA_NS['place_type_' + pnr_id]
            label = row['Paikanlajiryhmä']
            self.latest_group = entity_uri
            super_class = self.latest_theme
        elif row['Paikanlajialaryhmä_id']:
            pnr_id = str(int(row['Paikanlajialaryhmä_id']))
            entity_uri = PNR_SCHEMA_NS['place_type_' + pnr_id]
            label = row['Paikanlajialaryhmä']
            self.latest_subgroup = entity_uri
            super_class = self.latest_group
        elif row['Paikanlaji_id']:
            pnr_id = str(int(row['Paikanlaji_id']))
            # if pnr_id == '1020305':
            #     print(row['Kotus_661'])
            #     print(row['Kotus_662'])
            #     print(row['Kotus_663'])
            #     print(row['Kotus_664'])
            entity_uri = PNR_SCHEMA_NS['place_type_' + pnr_id]
            label = row['Paikanlaji']
            desc = row['Paikanlajin_kuvaus']
            super_class = self.latest_subgroup
            self.create_kotus_classes(row, entity_uri)
        else:
            return None


        row_rdf.add((entity_uri, RDF.type, self.instance_class))
        row_rdf.add((entity_uri, SKOS['prefLabel'], Literal(label, lang='fi')))

        if (super_class):
            row_rdf.add((entity_uri, RDFS['subClassOf'], super_class))
        if (desc):
            row_rdf.add((entity_uri, DCTERMS['description'], Literal(desc, lang='fi')))

        return row_rdf

    def create_kotus_classes(self, row, pnr_class):
        kotus_rdf = Graph()
        col_no = 1
        while row['Kotus_' + str(col_no)]:
             entity_uri = NA_SCHEMA_NS['place_type_' + str(self.kotus_id)]
             kotus_rdf.add((entity_uri, RDF.type, self.instance_class))
             kotus_rdf.add((entity_uri, RDFS['subClassOf'], pnr_class))
             label = row['Kotus_' + str(col_no)]

             if '/' in label:
                 parts = label.split('/')
                 prefLabel = parts[0].lower()
                 kotus_rdf.add((entity_uri, SKOS['prefLabel'], Literal(prefLabel, lang='fi')))
                 self.kotus_place_types[prefLabel] = self.kotus_id
                 for i in range(1, len(parts)):
                     kotus_rdf.add((entity_uri, SKOS['altLabel'], Literal(parts[i].lower(), lang='fi')))
                     self.kotus_place_types[parts[i]] = self.kotus_id
             else:
                 prefLabel = label.lower()
                 kotus_rdf.add((entity_uri, SKOS['prefLabel'], Literal(prefLabel, lang='fi')))
                 self.kotus_place_types[prefLabel] = self.kotus_id
             col_no += 1
             self.kotus_id += 1
        for x in range(1,15):
            if row['Kotus_' + str(col_no + x)] != '':
                print(row['Kotus_' + str(col_no + 1)])
        self.data += kotus_rdf

    def read_csv(self, csv_input):
        """
        Read in a CSV files using pandas.read_csv

        :param csv_input: CSV input (filename or buffer)
        """
        csv_data = pd.read_csv(csv_input, encoding='UTF-8', sep=',', na_values=[''])

        self.table = csv_data.fillna('').applymap(lambda x: x.strip() if type(x) == str else x)
        self.log.info('Data read from CSV %s' % csv_input)


    def serialize(self, output_dir):
        """
        Serialize RDF graphs

        :param destination_data: serialization destination for data
        :param destination_photographs: serialization destination for photo data
        :return: output from rdflib.Graph.serialize
        """
        bind_namespaces(self.data)
        ttl_destination = output_dir + "pnr-na-place-types.ttl"
        data = self.data.serialize(format="turtle", destination=ttl_destination)
        self.log.info('Data serialized to %s' % output_dir)

        dump(self.kotus_place_types, output_dir + 'na_place_types_for_linking.bin')
        return data  # Return for testing purposes

    def process_rows(self):
        """
        Loop through CSV rows and convert them to RDF
        """

        for index in range(len(self.table)):
            row_rdf = self.map_row_to_rdf(self.table.ix[index])
            if row_rdf:
                self.data += row_rdf

        # add place type hierarchy
        # place_type_hierarchy = Graph()
        #
        # place_type_hierarchy.add((URIRef(PLACE_TYPE_THEME), RDF.type, RDFS['Class']))
        # place_type_hierarchy.add((URIRef(PLACE_TYPE_THEME), SKOS['prefLabel'], Literal('Paikanlajiteema', lang='fi')))
        #
        # place_type_hierarchy.add((URIRef(PLACE_TYPE_GROUP), RDF.type, RDFS['Class']))
        # place_type_hierarchy.add((URIRef(PLACE_TYPE_GROUP), SKOS['prefLabel'], Literal('Paikanlajiryhmä', lang='fi')))
        # place_type_hierarchy.add((URIRef(PLACE_TYPE_GROUP), RDFS['subClassOf'], URIRef(PLACE_TYPE_THEME)))
        #
        # place_type_hierarchy.add((URIRef(PLACE_TYPE_SUBGROUP), RDF.type, RDFS['Class']))
        # place_type_hierarchy.add((URIRef(PLACE_TYPE_SUBGROUP), SKOS['prefLabel'], Literal('Paikanlajialaryhmä', lang='fi')))
        # place_type_hierarchy.add((URIRef(PLACE_TYPE_SUBGROUP), RDFS['subClassOf'], URIRef(PLACE_TYPE_GROUP)))
        #
        # place_type_hierarchy.add((URIRef(PLACE_TYPE), RDF.type, RDFS['Class']))
        # place_type_hierarchy.add((URIRef(PLACE_TYPE), SKOS['prefLabel'], Literal('Paikanlaji', lang='fi')))
        # place_type_hierarchy.add((URIRef(PLACE_TYPE), RDFS['subClassOf'], URIRef(PLACE_TYPE_SUBGROUP)))
        #
        # self.data += place_type_hierarchy


if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Process CSV", fromfile_prefix_chars='@')

    argparser.add_argument("input", help="Input CSV file")
    argparser.add_argument("output", help="Output location to serialize RDF files to")
    # argparser.add_argument("mode", help="CSV conversion mode", default="PNR", choices=["PNR"])
    argparser.add_argument("--loglevel", default='INFO', help="Logging level, default is INFO.",
                           choices=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

    args = argparser.parse_args()

    output_dir = args.output + '/' if args.output[-1] != '/' else args.output

    mapper = RDFMapper(None, RDFS['Class'], loglevel=args.loglevel.upper())
    mapper.read_csv(args.input)
    mapper.process_rows()
    mapper.serialize(output_dir)
