#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import logging
import subprocess
from os import listdir, path, remove, rename
from sys import argv, exit, stderr, stdout

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst as gst
import progressbar
import mutagen.oggtheora

from helpers import autovividict, filename_from_url, media, make_datestring
from model import session, setup_all, create_all, set_source, \
    Article, Category, Journal, SupplementaryMaterial
from sources import source_module
from helpers import config


def browse_database(target):
    filename = config.database_path(target)
    try:
        subprocess.call(['sqlitebrowser', filename])
    except OSError:
        stderr.write('Unable to start sqlitebrowser <http://sqlitebrowser.sourceforge.net/>.\n')
        exit(4)


def clear_media(target):
    media_raw_directory = config.get_media_refined_source_path(target)
    listing = listdir(media_raw_directory)

    metadata_refined_directory = config.get_metadata_refined_source_path(target)
    download_cache_path = path.join(metadata_refined_directory, 'download_cache')
    remove(download_cache_path)

    for filename in listing:
        media_path = path.join(media_raw_directory, filename)
        stderr.write(f"Removing “{media_path}” ... ")
        remove(media_path)
        stderr.write("done.\n")


def clear_database(target):
    filename = config.database_path(target)
    stderr.write(f"Removing “{filename}” ... ")
    try:
        remove(filename)
        stderr.write("done.\n")
    except OSError as e:
        stderr.write(f"\n{str(e)}\n")


def convert_media(target):
    materials = SupplementaryMaterial.query.filter_by(
        downloaded=True,
        converted=False
    ).all()
    for material in materials:
        media_refined_directory = config.get_media_refined_source_path(target)
        media_raw_directory = config.get_media_raw_source_path(target)
        temporary_media_path = path.join(media_refined_directory, 'current.ogg')

        filename = filename_from_url(material.url)
        media_raw_path = path.join(media_raw_directory, filename)
        media_refined_path = path.join(media_refined_directory, filename + '.ogg')

        if material.converting:
            stderr.write(f"Skipping conversion of “{media_raw_path}”, earlier attempt failed.\n")
            continue

        if path.isfile(media_refined_path):
            stderr.write(f"Skipping conversion of “{media_raw_path}”, exists at “{media_refined_path}”.\n")
            material.converted = True
            session.commit()
            continue

        material.converting = True
        session.commit()
        stderr.write(f"Converting “{media_raw_path}”, saving into “{media_refined_path}” ... ")

        m = media.Media(media_raw_path)
        try:
            m.find_streams()
            m.convert(temporary_media_path)
        except RuntimeError as e:
            logging.error(f"{e}: Skipping conversion of “{media_raw_path}”.")
            continue

        try:
            f = mutagen.oggtheora.OggTheora(temporary_media_path)
            for key, value in [
                ('TITLE', material.title),
                ('ALBUM', material.article.title),
                ('ARTIST', material.article.contrib_authors),
                ('COPYRIGHTS', material.article.copyright_holder),
                ('LICENSE', material.article.license_url),
                ('DESCRIPTION', material.caption),
                ('DATE', make_datestring(
                    material.article.year,
                    material.article.month,
                    material.article.day
                ))
