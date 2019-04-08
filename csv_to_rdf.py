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
import numpy as np
from decimal import *
f = FinnSyll()
from joblib import dump, load

class RDFMapper:
    """
    Map tabular data (currently pandas DataFrame) to RDF. Create a class instance of each row.
    """

    def __init__(self, mapping, instance_class, mode, loglevel='WARNING'):
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
        if mode == 'create_place_types':
            self.place_types_not_linked_to_pnr = {}
            self.kotus_place_types = {}
            self.latest_theme = None
            self.latest_group = None
            self.latest_subgroup = None
            self.kotus_id = 1

        if mode == 'create_places':
            self.kotus_place_types = load('output/kotus_place_types_temp.bin')
            self.place_types_not_linked_to_pnr = load('output/place_types_not_linked_to_pnr_temp.bin')

    def places_map_row_to_rdf(self, row):
        """
        Map a single row to RDF.

        :param row: tabular data
        :return:
        """

        row_rdf = Graph()
        mediawiki_id = row['wiki_id']

        if mediawiki_id == '':
            return None
        else:
            # URI of the instance being created
            entity_uri = NA_LDF_NS[mediawiki_id]

        # Loop through the mapping dict and convert the row to RDF
        for column_name in self.mapping:

            mapping = self.mapping[column_name]
            value = row[column_name]
            converter = mapping.get('converter')
            value = converter(value) if converter else value
            if value == '' or value is None:
                return None
            liter = None

            if (column_name == 'lat' or column_name == 'long'):
                value = Decimal(value)
                value = round(value, 6)
                liter = Literal(value)
            elif column_name == 'place_type':
                value = value.lower()
                if value in self.kotus_place_types:
                    #print('{value} found in PNR-Kotus mapping'.format(value=value))
                    kotus_id = self.kotus_place_types[value]
                    liter = NA_SCHEMA_NS['place_type_' + str(kotus_id)]
                elif value in self.place_types_not_linked_to_pnr:
                    #print('{value} found in Kotus unclassified list'.format(value=value))
                    liter = self.place_types_not_linked_to_pnr[value]
                else:
                    print('{value} not found in mapping lists'.format(value=value))
            elif column_name == 'wiki_id':
                liter = NA_NS[value]        
            else:
                liter = Literal(value)

            if liter:
                row_rdf.add((entity_uri, mapping['uri'], liter))

            # extra triples:
            if column_name == 'place_name':
                 # Use FinnSyll to split place name into modifier and basic element if possible
                 splitted = f.split(value)
                 if '=' in splitted:
                     lastIndex = splitted.rindex('=')+1
                     modifier = splitted[:lastIndex].replace('=', '')  # määriteosa
                     basic_element = splitted[lastIndex:] # perusosa
                     row_rdf.add((entity_uri, NA_SCHEMA_NS['place_name_modifier'], Literal(modifier)))
                     row_rdf.add((entity_uri, NA_SCHEMA_NS['place_name_basic_element'], Literal(basic_element)))
        # end column loop

        return row_rdf

    def place_types_map_row_to_rdf(self, row):
        """
        Map a single row to RDF.

        :param entity_uri: URI of the instance being created
        :param row: tabular data
        :return:
        """
        row_rdf = Graph()
        hipla_place_class = HIPLA_SCHEMA_NS['Place']

        row_rdf.add((hipla_place_class, RDF.type, self.instance_class))
        row_rdf.add((hipla_place_class, SKOS.prefLabel, Literal("Paikka", lang='fi')))
        row_rdf.add((hipla_place_class, SKOS.prefLabel, Literal("Paikka", lang='en')))
        super_class = None
        desc = None
        #print(row)

        if row['Paikanlajiteema_id']:
            pnr_id = str(int(row['Paikanlajiteema_id']))
            entity_uri = PNR_SCHEMA_NS['place_type_' + pnr_id]
            label = row['Paikanlajiteema']
            self.latest_theme = entity_uri
            row_rdf.add((entity_uri, RDFS['subClassOf'], HIPLA_SCHEMA_NS['Place']))
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
        while row['Kotus_' + str(col_no)] != '':
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
        #print('last column:')
        #print(row['Kotus_' + str(col_no - 1)])
        for x in range(1,15):
            col = col_no + x
            if  col < 1366 and row['Kotus_' + str(col)] != '':
               print(row['Kotus_' + str(col_no + 1)])
        self.data += kotus_rdf

    def read_csv(self, csv_input):
        """
        Read in a CSV files using pandas.read_csv

        :param csv_input: CSV input (filename or buffer)
        """
        # https://stackoverflow.com/a/45063514
        dtypes = {
            'lat': 'U',
            'long': 'U'
        }
        csv_data = pd.read_csv(csv_input, encoding='UTF-8', sep=',', na_values=[''], dtype=dtypes)

        self.table = csv_data.fillna('').applymap(lambda x: x.strip() if type(x) == str else x)
        self.log.info('Data read from CSV %s' % csv_input)
        #print('Data read from CSV %s' % csv_input)

    def place_types_read_csv(self, csv_input):
        """
        Read in a CSV files using pandas.read_csv

        :param csv_input: CSV input (filename or buffer)
        """
        csv_data = pd.read_csv(csv_input, encoding='UTF-8', sep=',', na_values=[''])
        self.table = csv_data.fillna('').applymap(lambda x: x.strip() if type(x) == str else x)
        self.log.info('Data read from CSV %s' % csv_input)

    def place_types_read_and_process_unclassified_csv(self):
        csv_data = pd.read_csv('source_data/2-Kotus-paikanlajit-ei-PNR-luokkaa - Sheet1.csv', encoding='UTF-8', sep=',', na_values=[''], dtype={'paikanlaji': 'U'})
        kotus_unclassified_rdf = Graph()

        # create custon classes for place types that could not be classified

        #appellative_uri = NA_SCHEMA_NS['place_type_appellative']
        #kotus_unclassified_rdf.add((appellative_uri, RDF.type, self.instance_class))
        #kotus_unclassified_rdf.add((appellative_uri, SKOS.prefLabel, Literal('Appellatiivi', lang='fi')))

        #person_name_uri = NA_SCHEMA_NS['place_type_person_name']
        #kotus_unclassified_rdf.add((person_name_uri, RDF.type, self.instance_class))
        #kotus_unclassified_rdf.add((person_name_uri, SKOS.prefLabel, Literal('Henkilönimi', lang='fi')))

        #other_name_uri = NA_SCHEMA_NS['place_type_other_name']
        #kotus_unclassified_rdf.add((other_name_uri, RDF.type, self.instance_class))
        #kotus_unclassified_rdf.add((other_name_uri, SKOS.prefLabel, Literal('Muu nimi', lang='fi')))

        unclassified_uri = NA_SCHEMA_NS['place_type_unclassified']
        kotus_unclassified_rdf.add((unclassified_uri, RDF.type, self.instance_class))
        kotus_unclassified_rdf.add((unclassified_uri, SKOS.prefLabel, Literal('Luokittelematon', lang='fi')))
        kotus_unclassified_rdf.add((unclassified_uri, RDFS.subClassOf, HIPLA_SCHEMA_NS['Place']))

        multiclass_uri = NA_SCHEMA_NS['place_type_multiclass']
        kotus_unclassified_rdf.add((multiclass_uri, RDF.type, self.instance_class))
        kotus_unclassified_rdf.add((multiclass_uri, SKOS.prefLabel, Literal('Monta paikkatyyppiä', lang='fi')))
        kotus_unclassified_rdf.add((multiclass_uri, RDFS.subClassOf, unclassified_uri))

        swedish_uri = NA_SCHEMA_NS['place_type_swedish']
        kotus_unclassified_rdf.add((swedish_uri, RDF.type, self.instance_class))
        kotus_unclassified_rdf.add((swedish_uri, SKOS.prefLabel, Literal('Ruotsinkielinen paikkatyyppi', lang='fi')))
        kotus_unclassified_rdf.add((multiclass_uri, RDFS.subClassOf, unclassified_uri))

        for index in range(len(csv_data)):
            row = csv_data.iloc[index]
            place_type = str(row['paikanlaji']).lower()
            if place_type not in self.place_types_not_linked_to_pnr:
                #if place_type.startswith('appellatiivi'):
                #    place_type = place_type.split('appellatiivi ')[1]
                #    self.place_types_not_linked_to_pnr[place_type] = appellative_uri
                #elif place_type.startswith('henkilönimi'):
                #    place_type = place_type.split('henkilönimi ')[1]
                #    self.place_types_not_linked_to_pnr[place_type] = person_name_uri
                #elif place_type.startswith('muut nimet'):
                #    place_type = place_type.split('muut nimet ')[1]
                #    self.place_types_not_linked_to_pnr[place_type] = other_name_uri
                if place_type.startswith('luokittelematon'):
                    place_type = place_type.split('luokittelematon ')[1]
                    place_type_uri = NA_SCHEMA_NS['place_type_' + str(self.kotus_id)]
                    kotus_unclassified_rdf.add((place_type_uri, RDF.type, self.instance_class))
                    kotus_unclassified_rdf.add((place_type_uri, SKOS['prefLabel'], Literal(place_type, lang='fi')))
                    kotus_unclassified_rdf.add((place_type_uri, RDFS['subClassOf'], unclassified_uri))
                    self.place_types_not_linked_to_pnr[place_type] = place_type_uri
                    self.kotus_id += 1
                elif place_type.startswith('monta paikkatyyppiä'):
                    place_type = place_type.split('monta paikkatyyppiä ')[1]
                    place_type_uri = NA_SCHEMA_NS['place_type_' + str(self.kotus_id)]
                    kotus_unclassified_rdf.add((place_type_uri, RDF.type, self.instance_class))
                    kotus_unclassified_rdf.add((place_type_uri, SKOS['prefLabel'], Literal(place_type, lang='fi')))
                    kotus_unclassified_rdf.add((place_type_uri, RDFS['subClassOf'], multiclass_uri))
                    self.place_types_not_linked_to_pnr[place_type] = place_type_uri
                    self.kotus_id += 1
                elif place_type.startswith('ruots'):
                    place_type = place_type.split('ruots ')[1]
                    place_type_uri = NA_SCHEMA_NS['place_type_' + str(self.kotus_id)]
                    kotus_unclassified_rdf.add((place_type_uri, RDF.type, self.instance_class))
                    kotus_unclassified_rdf.add((place_type_uri, SKOS['prefLabel'], Literal(place_type, lang='fi')))
                    kotus_unclassified_rdf.add((place_type_uri, RDFS['subClassOf'], swedish_uri))
                    self.place_types_not_linked_to_pnr[place_type] = place_type_uri
                    self.kotus_id += 1

        self.data += kotus_unclassified_rdf

    def serialize(self, destination_data, destination_schema):
        """
        Serialize RDF graphs

        :param destination_data: serialization destination for data
        :param destination_photographs: serialization destination for photo data
        :param destination_schema: serialization destination for schema
        :return: output from rdflib.Graph.serialize
        """
        bind_namespaces(self.data)
        bind_namespaces(self.schema)

        data = self.data.serialize(format="turtle", destination=destination_data)
        schema = self.schema.serialize(format="turtle", destination=destination_schema)

        self.log.info('Data serialized to %s' % destination_data)
        self.log.info('Schema serialized to %s' % destination_schema)

        return data, schema  # Return for testing purposes

    def place_types_serialize(self, output_dir):
        """
        Serialize RDF graphs

        :param destination_data: serialization destination for data
        :param destination_photographs: serialization destination for photo data
        :return: output from rdflib.Graph.serialize
        """
        bind_namespaces(self.data)
        ttl_destination = output_dir + "kotus-names-archive-placetypes.ttl"
        data = self.data.serialize(format="turtle", destination=ttl_destination)
        self.log.info('Data serialized to %s' % output_dir)

        dump(self.kotus_place_types, output_dir + 'kotus_place_types_temp.bin')
        dump(self.place_types_not_linked_to_pnr, output_dir + 'place_types_not_linked_to_pnr_temp.bin')
        # return data  # Return for testing purposes

    def places_process_rows(self):
        """
        Loop through CSV rows and convert them to RDF
        """

        for index in range(len(self.table)):
            row_rdf = self.places_map_row_to_rdf(self.table.iloc[index])
            if row_rdf is not None:
                self.data += row_rdf

        # generate schema RDF
        for prop in self.mapping.values():

            if 'uri' in prop:
                self.schema.add((prop['uri'], RDF.type, RDF.Property))
                if 'name_fi' in prop:
                    self.schema.add((prop['uri'], SKOS.prefLabel, Literal(prop['name_fi'], lang='fi')))
                if 'name_en' in prop:
                    self.schema.add((prop['uri'], SKOS.prefLabel, Literal(prop['name_en'], lang='en')))
            else:
                continue

    def place_types_process_rows(self):
        """
        Loop through CSV rows and convert them to RDF
        """

        for index in range(len(self.table)):
            row_rdf = self.place_types_map_row_to_rdf(self.table.iloc[index])
            if row_rdf is not None:
                self.data += row_rdf

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Process CSV", fromfile_prefix_chars='@')
    argparser.add_argument("--loglevel", default='INFO', help="Logging level, default is INFO.",
                           choices=["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    args = argparser.parse_args()

    output_dir = 'output/'

    # First create mapping from Names Archive place types to Place Name Register place types
    place_types_input = 'source_data/1-PNR-Kotus-paikanlajit - Sheet1.csv'
    mapper = RDFMapper(None, RDFS['Class'], 'create_place_types', loglevel=args.loglevel.upper())
    mapper.place_types_read_csv(place_types_input)
    print('Data read from CSV %s' % place_types_input)
    mapper.place_types_process_rows()
    mapper.place_types_read_and_process_unclassified_csv()
    mapper.place_types_serialize(output_dir)
    print('Place types serialized to %s' % output_dir)

    # Then convert the Names Archive CSV dump into RDF
    places_input = 'source_data/nimiarkisto.fi-CC-BY-4.0_2019-03-29_1000.csv'
    mapper = RDFMapper(KOTUS_MAPPING, HIPLA_SCHEMA_NS['Place'], 'create_places', loglevel=args.loglevel.upper())
    mapper.read_csv(places_input)
    print('Data read from CSV %s' % places_input)
    mapper.places_process_rows()
    mapper.serialize(output_dir + "kotus-names-archive.ttl", output_dir + "kotus-names-archive-schema.ttl")
    print('Names archive data and schema serialized to %s' % output_dir)
