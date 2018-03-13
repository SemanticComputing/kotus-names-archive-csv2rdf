#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Define common RDF namespaces
"""
from rdflib import Namespace, RDF, RDFS, XSD

SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
WGS84 = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')

DATA_NS = Namespace('http://ldf.fi/kotus-digital-names-archive/')
SCHEMA_NS = Namespace('http://ldf.fi/schema/hipla/')

def bind_namespaces(graph):
    graph.bind("skos", "http://www.w3.org/2004/02/skos/core#")
    graph.bind("k", "http://ldf.fi/kotus/")
    graph.bind("hipla", "http://ldf.fi/schema/hipla/")
    graph.bind("wgs84", "http://www.w3.org/2003/01/geo/wgs84_pos#")
