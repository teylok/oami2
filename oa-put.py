#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from os import path
from sys import argv, stderr
from time import sleep
from urllib.parse import urlparse

from helpers import config, efetch, filename_from_url, mediawiki, template
from model import session, setup_all, create_all, set_source, \
    Article, Journal, SupplementaryMaterial

try:
    action = argv[1]
    target = argv[2]
except IndexError:  # no arguments given
    stderr.write("""
oa-put – Open Access Importer upload operations

usage:  oa-put upload-media [source]

""")
    exit(1)

try:
    assert action in ['upload-media']
except AssertionError:  # invalid action
    stderr.write("Unknown action “%s”.\n" % action)
    exit(2)

try:
    exec("from sources import %s as source_module" % target)
except ImportError:  # invalid source
    stderr.write("Unknown source “%s”.\n" % target)
    exit(3)

set_source(target)
setup_all(True)

if action == 'upload-media':
    media_refined_directory = config.get_media_refined_source_path(target)

    materials = SupplementaryMaterial.query.filter_by(
        converted=True,
        uploaded=False
    ).all()
    for material in materials:
        filename = filename_from_url(material.url) + '.ogg'
        media_refined_path = path.join(media_refined_directory, filename)

        if (path.getsize(media_refined_path) == 0):
            material.converted = False
            continue

        if mediawiki.is_uploaded(material):
            stderr.write("Skipping “%s”, already exists at %s.\n" % (
                media_refined_path.encode('utf-8'),
                mediawiki.get_wiki_name()
            ))
            material.uploaded = True
            continue

        article_doi = material.article.doi
        article_pmid = efetch.get_pmid_from_doi(article_doi)
        article_pmcid = efetch.get_pmcid_from_doi(article_doi)
        authors = material.article.contrib_authors
        article_title = material.article.title
        journal_title = material.article.journal.title
        article_year = material.article.year
        article_month = material.article.month
        article_day = material.article.day
        article_url = material.article.url
        license_url = material.article.license_url
        rights_holder = material.article.copyright_holder
        label = material.label
        title = material.title
        caption = material.caption
        mimetype = material.mimetype
        material_url = material.url
        categories = [category.name for category in material.article.categories]
        if article_pmid is not None:
            categories += efetch.get_categories_from_pmid(article_pmid)

        # TODO: file extension should be adapted for other file formats
        url_path = urlparse(material.url).path
        source_filename = url_path.split('/')[-1]
        assert mimetype in ('audio', 'video')
        if mimetype == 'audio':
            extension = 'oga'
        elif mimetype == 'video':
            extension = 'ogv'
        wiki_filename = path.splitext(source_filename)[0] + '.' + extension
        if article_title is not
