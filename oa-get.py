#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import progressbar
import magic
from os import path
from sys import argv, stderr
from urllib.request import urlopen, Request
from urllib.error import HTTPError

BUFSIZE = 1024000  # (1024KB)

from model import session, setup_all, create_all, set_source, Article, Journal, SupplementaryMaterial
from sources import sources_module
from helpers import config, mediawiki, filename_from_url

try:
    action = argv[1]
    target = argv[2]
except IndexError:  # no arguments given
    stderr.write("""
oa-get – Open Access Media Importer download operations

usage:  oa-get detect-duplicates [source] |
        oa-get download-metadata [source] |
        oa-get download-media [source] |
        oa-get update-mimetypes [source]

""")
    exit(1)

try:
    assert(action in ['detect-duplicates', 'download-media', 'download-metadata', 'update-mimetypes'])
except AssertionError:  # invalid action
    stderr.write("Unknown action “%s”.\n" % action)
    exit(2)

try:
    source_module = getattr(sources_module, target)
except AttributeError:  # invalid source
    stderr.write("Unknown source “%s”.\n" % target)
    exit(3)

set_source(target)
setup_all(True)

if action == 'detect-duplicates':
    materials = SupplementaryMaterial.query.filter(
        (SupplementaryMaterial.mimetype_reported == 'audio') |
        (SupplementaryMaterial.mimetype_reported == 'video')
    ).all()
    if len(materials) == 0:
        stderr.write('No audio or video materials found.\n')
        exit(5)
    for material in materials:
        if mediawiki.is_uploaded(material):
            stderr.write('[X] {} {} {}\n'.format(
                material.article.doi,
                material.title,
                material.label
            ))
        else:
            stderr.write('[ ] {} {} {}\n'.format(
                material.article.doi,
                material.title,
                material.label
            ))

if action == 'update-mimetypes':
    ms = magic.Magic(mime=True)
    materials = SupplementaryMaterial.query.filter_by(
        mimetype_reported=None,
        mime_subtype_reported=None
    ).all()
    free_materials = [
        material for material in materials
        if material.article.license_url in config.free_license_urls
    ]
    materials = free_materials  # Checking MIME types of non-free
    # supplementary materials costs time.
    stderr.write('Checking MIME types …\n')
    try:
        widgets = [
            progressbar.SimpleProgress(), ' ',
            progressbar.Percentage(), ' ',
            progressbar.Bar(), ' ',
            progressbar.ETA()
        ]
        p = progressbar.ProgressBar(
            max_value=len(materials),
            widgets=widgets
        ).start()
    except AssertionError:
        stderr.write('No materials found where MIME type has to be checked.\n')
        exit(0)
    for i, material in enumerate(materials):
        url = material.url
        request = Request(url, None, {'User-Agent': 'oa-get/2012-10-26'})
        request.headers['Range'] = 'bytes=%s-%s' % (0, 11)
        # 12 bytes should be enough to detect audio or video resources
        # <http://mimes
