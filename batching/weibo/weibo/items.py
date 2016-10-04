# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy_djangoitem import DjangoItem

import sys

sys.path.append('/home/jonas/PycharmProjects/demo')

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'demo.settings'
import django

django.setup()

from batching.models import Comment


class WeiboItem(DjangoItem):
    django_model = Comment
