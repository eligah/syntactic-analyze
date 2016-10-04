# coding:utf-8
from __future__ import unicode_literals

from django.contrib import admin
from django.db import models

# Create your models here.
from django.utils import timezone


class Comment(models.Model):
    userID = models.CharField(max_length=100)
    userName = models.CharField(max_length=100)
    userType = models.CharField(max_length=100)
    time = models.CharField(max_length=100)
    forwardNum = models.IntegerField(null=True)
    commentNum = models.IntegerField(null=True)
    likeNum = models.IntegerField(null=True)
    content = models.CharField(max_length=800)
    topicId = models.IntegerField(null=True)


class Keyword(models.Model):
    keyword_text = models.CharField(max_length=20)
    create_date = models.DateTimeField('create date', default=timezone.now)
    request_date = models.DateTimeField('date requested', default=timezone.now)
    request_count = models.PositiveIntegerField('count', default=0)
    diagram_data = models.TextField('lexical tree', null=True)
    # cloud_csv = models.FileField("cloud csv")
    # radar_csv = models.FileField("radar csv")

    def __str__(self):
        return self.keyword_text

    def __unicode__(self):
        return u'%s' % self.keyword_text


class KeywordAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['keyword_text', 'request_count']}),
        ('Date Info.', {'fields': ['request_date']})
    ]
    list_display = ('keyword_text', 'request_date', 'request_count')
    search_fields = ['keyword_text']


admin.site.register(Keyword, KeywordAdmin)
