# -*- coding: utf-8 -*-
"""
This file provides a new command to your shell for launching
your scrapy spiders from Django. It can be run like so:

>>> manage.py scrapy <spidername>

"""
from __future__ import absolute_import
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def run_from_argv(self, argv):
        self._argv = argv
        return super(Command, self).run_from_argv(argv)
    
    def handle(self, *args, **options):
        from scrapy.cmdline import execture
        execute(self._argv[1:])

import os
os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapy_project.settings'

