#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from datetime import datetime
import requests
from sys import stderr, stdout
from xml.etree.ElementTree import ElementTree

parser = ArgumentParser(
    description='List PMC IDs for articles in the PubMed Central Open Access subset.',
    epilog='Caveat: All dates are given in local time in Bethesda, Maryland: either EST (-05:00) or EDT (-04:00), depending on the time of year.'
)
parser.add_argument('--from', help='Only list articles updated on or after the specified date (YYYY-MM-DD).', type=str)
parser.add_argument('--until', help='Only list articles updated before the specified date (YYYY-MM-DD).', type=str)
parser.add_argument('--verbose', help='Output a dot to stderr for each successful HTTP request. Output a dash to stderr for each unsuccessful HTTP request.', dest='verbose', action='store_true')
args = parser.parse_args()
verbose = args.verbose

def parse_date(text):
    return datetime.strptime(text, '%Y-%m-%d').date()

def get_records(url):
    while url:
        try:
            response = requests.get(url, timeout=3)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            if verbose:
                stderr.write('-')
            continue
        except requests.exceptions.RequestException:
            if verbose:
                stderr.write('-')
            continue
        
        if verbose:
            stderr.write('.')
        tree = ElementTree()
        tree.parse(response.text)
        for record in tree.iterfind('*//record'):
            yield record
        resumption_link = tree.find('*//resumption/link')
        if resumption_link is not None:
            url = resumption_link.attrib['href']
        else:
            url = None

date_from = parse_date(args.__getattribute__('from'))  # reserved word
date_until = parse_date(args.until)
url = 'http://www.pubmedcentral.nih.gov/utils/oa/oa.fcgi?from=%s&until=%s' \
    % (date_from.isoformat(), date_until.isoformat())

records = get_records(url)
for record in records:
    stdout.write(record.attrib['id'])
    stdout.write(' ')
