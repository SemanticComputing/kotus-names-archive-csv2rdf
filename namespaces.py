#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Define common RDF namespaces
"""
from rdflib import Namespace, RDF, RDFS, XSD

SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
DCTERMS = Namespace('http://purl.org/dc/terms/')
WGS84 = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')

NA_NS = Namespace('http://ldf.fi/kotus-digital-names-archive/')
HIPLA_SCHEMA_NS = Namespace('http://ldf.fi/schema/hipla/')
PNR_SCHEMA_NS = Namespace('http://ldf.fi/schema/pnr/')
NA_SCHEMA_NS = Namespace('http://ldf.fi/schema/na/')

def bind_namespaces(graph):
    graph.bind("skos", "http://www.w3.org/2004/02/skos/core#")
    graph.bind("dcterms", "http://purl.org/dc/terms/")
    graph.bind("wgs84", "http://www.w3.org/2003/01/geo/wgs84_pos#")

    graph.bind("na", "http://ldf.fi/kotus-digital-names-archive/")
    graph.bind("pnr-schema", "http://ldf.fi/schema/pnr/")
    graph.bind("na-schema", "http://ldf.fi/schema/kotus/")
    graph.bind("hipla-schema", "http://ldf.fi/schema/hipla/")
    
