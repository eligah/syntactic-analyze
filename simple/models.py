# coding:utf-8
from __future__ import unicode_literals

import json
import urllib2
from urllib import urlencode

from django.contrib import admin
from django.core.validators import MinLengthValidator
from django.db import models

# Create your models here.
from django.utils import timezone
import jieba.posseg as pseg
import re

from simple.algorithm import judge
from simple.algorithm.syntacticAnalysis import SyntacticAnalysis



def wash_data(text):
    text = re.sub('【[^【】]*】', '', text)  # 去除包含在【……】中的内容
    text = re.sub('【[^【?]*?', '', text)  # 去除包含在【……?中的内容
    text = re.sub('【[^【？]*？', '', text)  # 去除包含在【……？中的内容
    text = re.sub('#[^#]*#', '', text)  # 去除包含在#……#中的内容
    text = re.sub('//@[^：]*：', '', text)  # 去除//@……：中的内容
    text = re.sub('//@[^:]*:', '', text)  # 去除//@……: 中的内容
    text = re.sub('@[^ \t]*[ \t]', '', text)  # 去除@后跟部分直到遇到制表符或者空格
    text = re.sub('^[^【】]*】', '', text)  # 若文本中仅有】而没有【，则去除】之前的所有部分
    text = re.sub('《[^《》]*》', '', text)  # 去除包含在《……》中的内容
    text = re.sub('（[^（）]*）', '', text)  # 去除（……）中的内容
    text = re.sub('……', '，', text)  # 将“……”替换为“，”（此处须为完整的中文省略号）
    text = re.sub('[；;]', '，', text)  # 将“；”和“;”替换为“，”
    text = re.sub('\"[^\"]*\"', '', text)  # 去除双引号内的所有内容
    text = re.sub('“[^“”]*”', '', text)  # 去除双引号内的所有内容
    text = re.sub(
        '^(((http|https|ftp)://)?([[a-zA-Z0-9]\-\.])+(\.)([[a-zA-Z0-9]]){2,4}([[a-zA-Z0-9]/+=%&_\.~?\-]*))*$',
        '', text)  # 去除网址
    # text = re.sub('\[[^\[\]]*\]', '', text)  # 去除中括号括起来的部分
    # text = re.sub('(\d)(O|o|〇)(?=\d)', '\\g<1>0', text)  # 替换数字间写错的零成：0
    return text


class Simple(models.Model):
    sentence_text = models.CharField(max_length=200, unique=True, null=False, validators=[MinLengthValidator(1)])
    preprocess_sen = models.CharField(max_length=200, null=True)
    pos_tagging = models.CharField(max_length=200, null=True)
    lexical_tree = models.TextField('lexical tree', null=True)
    request_date = models.DateTimeField('date requested', default=timezone.now)
    request_count = models.PositiveIntegerField('count', default=0)
    pv_word = models.TextField("pv word", null=True)
    pv_modifier_word = models.TextField("pv modifier word", null=True)
    keywords = models.TextField("keywords", null=True)
    emotion = models.IntegerField('emotion', default=-1)

    def __str__(self):
        return self.sentence_text

    def __unicode__(self):
        return u'%s' % self.sentence_text

    def get_washed_text(self, refresh=False):
        """
        获取预处理后的数据
        :param refresh: 如果refresh设置为True，则强制进行依次预处理，再返回结果
        :return: 第一次调用会进行一次预处理，并把结果存入数据库，之后调用将直接从数据库读取结果
        """
        if self.preprocess_sen is None or refresh:
            self.preprocess_sen = wash_data(self.sentence_text)
            self.save()
        print "washed text :%s" % self.preprocess_sen
        return self.preprocess_sen

    def get_seg_json(self, refresh=False):
        """
        获取jieba分词结果的json格式
        :param refresh: 是否强制重新分词，并刷新分词结果
        :return: jieba分词
        """
        if self.pos_tagging is None or refresh:
            words = pseg.cut(self.get_washed_text())
            self.pos_tagging = ''
            for word, flag in words:
                self.pos_tagging += (word + flag[0] + ',')
            self.pos_tagging = self.pos_tagging[:-1]
            self.save()
        return self.pos_tagging

    def get_lexical_tree(self, refresh=False):
        """
        获取词法分析树的数据（调用哈工大云的API）
        :param refresh: 是否强制刷新数据，是则重新调用哈工大云API
        :return: 词法分析树的json格式数据
        """
        if self.lexical_tree is None or len(self.lexical_tree) == 0 or refresh:
            text = self.get_washed_text()
            params = {
                'api_key': 'N5G9s2d6TVoT7mptglCmWagXJqWWKAfBMBlDxJBR',
                'text': text.encode('utf8'), 'format': 'json', 'pattern': 'all'}

            params = urlencode(params)
            url = "http://api.ltp-cloud.com/analysis/?" + params
            result = urllib2.urlopen(url)
            content = result.read().strip()
            content = re.sub('\n', ' ', content.decode('utf8')).encode('utf8')

            self.lexical_tree = content
            self.save()

        print self.lexical_tree
        return self.lexical_tree

    def get_lexical_tree_strip(self):
        content = self.get_lexical_tree()
        content = json.loads(content)[0][0]
        content = json.dumps(content)
        return content

    def syntactic(self):
        """
        call API from algorithm to tell the syntactic of this sentence
        :return: Negative, Declarative or Question
        """

        if self.emotion < 0:
            washed = self.get_washed_text()
            segs = self.get_seg_json()
            ltp = self.get_lexical_tree_strip()
            ltp_list = []
            ltp_list.append(ltp.encode('utf8'))
            washed_list = []
            washed_list.append(washed.encode('utf8'))
            segs_list = []
            segs_list.append(segs.encode('utf8'))
            id_list = []
            id_list.append(self.id)

            # hgd_file 是指经过哈工大预处理后的句子
            # test_numark_file 是指没有处理过的句子
            # test_file 是指分词后句子

            result = judge.test(washed_list, segs_list, ltp_list, id_list)
            if result is None:
                self.emotion = -1
            else:
                self.emotion = result
            self.save()
        if self.emotion == 0:
            return '疑问句'
        if self.emotion == 1:
            return '否定句'
        if self.emotion == 2:
            return '陈述句'
        return self.emotion


class SentenceAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['sentence_text', 'request_count', 'washed_text', 'seg_json', 'lexical_tree', 'emotion']}),
        ('Date Info.', {'fields': ['request_date']})
    ]
    list_display = ('sentence_text', 'request_date', 'emotion', 'request_count')
    search_fields = ['sentence_text']


admin.site.register(Simple, SentenceAdmin)
