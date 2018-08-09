#!/usr/bin/env python3
#  -*- coding: UTF-8 -*-
"""
Converters for CSV cell data
"""

import datetime
import logging
import re
import requests

from rdflib import Graph, Literal
from slugify import slugify

from namespaces import *

log = logging.getLogger(__name__)


def convert_int(raw_value: str):
    """
    Convert string value to integer if possible, if not, return original value

    :param raw_value: original string value
    :return: converted or original value
    """
    if not raw_value:
        return raw_value
    try:
        value = int(raw_value)  # This cannot be directly converted on the DataFrame because of missing values.
        log.debug('Converted int: %s' % raw_value)
        return value
    except (ValueError, TypeError):
        log.warning('Invalid value for int conversion: %s' % raw_value)
        return raw_value


def convert_dates(raw_date: str):
    """
    Convert date string to iso8601 date

    :param raw_date: raw date string from the CSV
    :return: ISO 8601 compliant date if can be parse, otherwise original date string
    """
    if not raw_date:
        return raw_date
    try:
        date = datetime.datetime.strptime(str(raw_date).strip(), '%d/%m/%Y').date()
        log.debug('Converted date: %s  to  %s' % (raw_date, date))
        return date
    except ValueError:
        try:
            date = datetime.datetime.strptime(str(raw_date).strip(), '%d.%m.%Y').date()
            log.debug('Converted date: %s  to  %s' % (raw_date, date))
            return date
        except ValueError:
            log.warning('Invalid value for date conversion: %s' % raw_date)
        return raw_date


def strip_dash(raw_value: str):
    return '' if raw_value.strip() == '-' else raw_value


def add_trailing_zeros(raw_value):
    i = convert_int(raw_value)
    return format(i, '03d')
