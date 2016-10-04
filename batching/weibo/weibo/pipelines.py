# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy import log
from twisted.enterprise import adbapi

import MySQLdb
import MySQLdb.cursors


class WeiboPipeline(object):
    def __init__(self):
        self.file = codecs.open('weibo.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()


class MySQLWeiboPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
        return cls(dbpool)

    # pipeline默认调用
    def process_item(self, item, spider):
        d = self.dbpool.runInteraction(self._do_insert, item, spider)
        d.addErrback(self._handle_error, item, spider)
        d.addBoth(lambda _: item)
        return d

    # 将每行更新或写入数据库中
    def _do_insert(self, conn, item, spider):
        # conn.execute("""
        #                 INSERT INTO comment (userID, userName, userType, time, forwardNum, commentNum, likeNum, content, title, usercard)
        # VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        #             """, (item['userID'], item['userName'], item['userType'],
        #                   item['time'], item['forwardNum'], item['commentNum'],
        #                   item['likeNum'], item['content'], item['title'], item['usercard']))
        conn.execute("""
                        INSERT INTO Comment (userID, userName, time, forwardNum, commentNum, likeNum, content)
        VALUES (%s,%s,%s,%s,%s,%s,%s);
                    """, (item['userID'], item['userName'], item['time'],
                          item['forwardNum'], item['commentNum'], item['likeNum'], item['content']))

    # 异常处理
    @staticmethod
    def _handle_error(failure, item, spider):
        log.err(failure)
