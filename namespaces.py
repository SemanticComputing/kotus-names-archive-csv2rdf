#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Define common RDF namespaces
"""
from rdflib import Namespace, RDF, RDFS, XSD

SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
DCTERMS = Namespace('http://purl.org/dc/terms/')
WGS84 = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')

NA_NS = Namespace('https://nimiarkisto.fi/wiki/')
NA_LDF_NS = Namespace('http://ldf.fi/kotus-names-archive/')

HIPLA_SCHEMA_NS = Namespace('http://ldf.fi/schema/hipla/')
PNR_SCHEMA_NS = Namespace('http://ldf.fi/schema/pnr/')
NA_SCHEMA_NS = Namespace('http://ldf.fi/schema/kotus-names-archive/')

def bind_namespaces(graph):
    graph.bind("skos", SKOS)
    graph.bind("dcterms", DCTERMS)
    graph.bind("wgs84", WGS84)
    graph.bind("owl", OWL)
    graph.bind("na", NA_LDF_NS)
    graph.bind("hipla-schema", HIPLA_SCHEMA_NS)
    graph.bind("pnr-schema", PNR_SCHEMA_NS)
    graph.bind("na-schema", NA_SCHEMA_NS)
