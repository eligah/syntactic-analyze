#!/usr/bin/env python
# -*- coding: utf-8 -*-


import MySQLdb
import chardet
import time

import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class BatchAnalyze:
    def __init__(self, host='localhost', user='root', passwd='1234'):
        # connect Database
        self.conn = MySQLdb.connect(host, user, passwd)
        self.conn.set_character_set('utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')
        # select database
        self.conn.select_db('demo')

        # stop word list
        self.stopword_list = []
        self.readStopword()

        # about database
        self.db_feature_set = []
        self.db_key_feature = ur''
        self.db_time_set = ur''

    # 读取停词表
    def readStopword(self):
        input_f = open('../../dataFolder/stopWord.txt')
        sen_list = input_f.readlines()
        for temp_sen in sen_list:
            self.stopword_list.append(temp_sen.strip())
        input_f.close()

        # for i in range(0, len(self.stopword_list)):
        #     print self.stopword_list[i]

    # 读取批量分析的数据
    def analyzeBatchData(self, topic_name):
        self.batch_unmark_list = []
        self.batch_data_list = []
        self.batch_label_list = []
        self.batch_time_list = []

        sql = "select * from batch_data where topicName = '%s' " % topic_name
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        self.topic_name = topic_name
        self.topic_id = results[0][4]
        for temp_data in results:
            self.batch_unmark_list.append(temp_data[1])
            self.batch_data_list.append(temp_data[2])
            self.batch_label_list.append(temp_data[3])
            # print temp_data[2]

        self.sentence_count = len(self.batch_data_list)

        self.getFrequentFeatures()
        self.getKeyFeatures()
        self.analyzekeyFeatures()
        self.updataResults()

    #  做基础的时间统计
    def timeBaseCount(self):
        # get the base time
        min_time = self.news_list_news_time[0]
        max_time = self.news_list_news_time[0]
        for i in range(0, self.news_count):
            if self.news_list_news_time[i] > max_time:
                max_time = self.news_list_news_time[i]
            elif self.news_list_news_time[i] < min_time and self.news_list_news_time[i] != 0:
                min_time = self.news_list_news_time[i]

        print min_time, max_time
        print time.localtime(min_time)
        print time.localtime(max_time)

        # caclulate total day
        self.base_time = min_time - time.localtime(min_time).tm_hour * 3600 - time.localtime(
            min_time).tm_min * 60 - time.localtime(min_time).tm_sec
        print self.base_time
        self.total_day = (max_time - self.base_time) / data_length + 1

    # 时序分析，产生时间-正反评价图
    def timeAnalyze(self):
        print "count based on time"
        self.total_day = 0
        self.base_time = 0
        self.timeBaseCount()

        self.day_count_good = []
        self.day_count_bad = []
        for i in range(0, self.total_day):
            self.day_count_good.append(0)
            self.day_count_bad.append(0)
        for i in range(0, self.sentence_count):
            day = (self.batch_time_list[i] - self.base_time) / 86400
            if self.batch_label_list[i] == 2:
                self.day_count_good[day] += 1
            elif self.batch_label_list[i] == 1:
                self.day_count_bad[day] += 1

        output_f = open(ur'dataFolder\batch\dayAnalyze.txt', 'w')
        for i in range(0, self.total_day):
            output_f.write('%d,%d,%d\n' % (i, self.day_count_good[day], self.day_count_bad[day]))
        output_f.close()

        # # count
        # self.comment_day_count = []
        # for i in range(0, self.total_day):
        #     self.comment_day_count.append(0)
        # for i in range(0, self.comment_count):
        #     day = (self.comment_list_time[i] - self.base_time)/86400
        #     self.comment_day_count[day] += 1
        #     self.comment_list_day_index[i] = day
        #
        # output_f = open(ur'dataFolder\comment_day_count.csv', 'w')
        # index = 0
        # for i in range(0, self.total_day):
        #     sec_time = self.base_time + 86400*i
        #     str_time = time.strftime("%Y-%m-%d",time.localtime(sec_time))
        #     output_f.write('%s,%s\n' % (str_time,self.comment_day_count[i]))
        # output_f.close()
        #
        # # str = '2015-12-15 00:00:00'
        # # str_time = time.strptime(str, "%Y-%m-%d %H:%M:%S")
        # # sec_time = int(time.mktime(str_time))
        # # print sec_time

    # 获取陈述句（正面）、否定句（反面）、疑问句 的频繁特征， 用于绘制字云图
    def getFrequentFeatureOld(self):
        self.max_frequent_feature = []

        self.cluster_count = []
        self.cluster_feature_dict = [dict() for i in range(0, 3)]
        print self.sentence_count

        # sentence_list = []

        for j in range(0, 3):
            self.cluster_count.append(0)
            # sentence_list.append('')
            for i in range(0, self.sentence_count):
                if self.label_list[i] == j:
                    self.cluster_count[j] += 1
                    print i, self.sentence_list[i]
                    words = self.sentence_list[i].split(',')
                    for w in words:
                        word = w[:-1]
                        flag = w[-1]
                        print word, flag
                        if (flag == 'n') and len(word) >= 6:
                            if word not in self.stopword_list:
                                # sentence_list[j] += word
                                if self.cluster_feature_dict[j].has_key(word):
                                    self.cluster_feature_dict[j][word] += 1
                                else:
                                    self.cluster_feature_dict[j][word] = 1

            file_name = (ur'dataFolder\pre_topic_results\cluster_feature_dict_%d.csv' % j)
            output_f = open(file_name, 'w')
            test = sorted(self.cluster_feature_dict[j].iteritems(), key=lambda d: d[1], reverse=True)

            # fwords = jieba.analyse.extract_tags(sentence_list[j],10)
            # for i in range(0, 10):
            #     print fwords[i], test[i][0]


            count = 0
            for i in range(0, 10):
                if test[i][0] not in self.max_frequent_feature:
                    self.max_frequent_feature.append(test[i][0])
                    count += 1
                    if count > 2:
                        break

            max_frequent = test[0][1] / 110.0
            output_f.write('%d\n' % self.cluster_count[j])
            for word, value in test:
                output_f.write('%s,%f\n' % (word, value / max_frequent))
            output_f.close()

        # for w in self.max_frequent_feature:
        #     print w
        self.featureAnalyze(self.max_frequent_feature)

    # 获取陈述句（正面）、否定句（反面）、疑问句 的频繁特征， 用于绘制字云图
    def getFrequentFeatures(self):
        print 'Get Frequent Features'

        self.cluster_count = []
        self.cluster_feature_dict = [dict() for i in range(0, 3)]

        # 备选关键特征
        self.backup_key_features = [[] for i in range(0, 3)]
        self.backup_key_features_count = [[] for i in range(0, 3)]

        for j in range(0, 3):
            self.cluster_count.append(0)
            for i in range(0, self.sentence_count):
                if self.batch_label_list[i] == j:
                    self.cluster_count[j] += 1
                    words = self.batch_data_list[i].split(',')

                    for temp in words:
                        if temp == '':
                            continue
                        w = temp.split('^')
                        word = w[0]
                        flag = w[1]
                        if len(flag) == 0 or len(word) == 0:
                            continue
                        # print word, flag, len(flag), len(word)
                        if (flag[0] == 'n' or flag[0] == 'v' or flag[0] == 'a') and len(word) >= 6:
                            if word not in self.stopword_list:
                                # sentence_list[j] += word
                                if self.cluster_feature_dict[j].has_key(word):
                                    self.cluster_feature_dict[j][word] += 1

                                else:
                                    self.cluster_feature_dict[j][word] = 1

                                # 构建备选关键特征集
                                if flag[0] == 'n':
                                    add_num = 1
                                    if len(flag) > 1:
                                        add_num = 2
                                    if word in self.backup_key_features[j]:
                                        index = self.backup_key_features[j].index(word)
                                        self.backup_key_features_count[j][index] += add_num
                                    else:
                                        self.backup_key_features[j].append(word)
                                        self.backup_key_features_count[j].append(add_num)

        for j in range(0, 3):
            # self.total_feature_frequent.append(0)
            for word, value in self.cluster_feature_dict[j].items():
                # self.total_feature_frequent[j] += value
                count = value
                for t in range(0, 3):
                    if t != j:
                        if self.cluster_feature_dict[t].has_key(word):
                            count += self.cluster_feature_dict[t][word]
                self.cluster_feature_dict[j][word] = value * value * 1.0 / count

        for j in range(0, 3):
            self.db_feature_set.append('')
            test = sorted(self.cluster_feature_dict[j].iteritems(), key=lambda d: d[1], reverse=True)
            max_frequent = test[0][1] / 110.0

            feature_count = 0
            for word, value in test:
                # if chardet.detect(word)['encoding'] != 'utf-8':
                #     print word, chardet.detect(word)
                #     continue
                temp_str = '%s^%s,' % (word.encode('utf-8'), value / max_frequent)
                self.db_feature_set[j] += temp_str
                feature_count += 1
                if feature_count > 100:
                    break
            self.db_feature_set[j] = self.db_feature_set[j][:-1]
            # print self.db_feature_set[j]

    # 获取特定维度的关键特征值词
    def getKeyFeatures(self):
        print 'get Key Features'

        self.max_frequent_feature = []
        self.backup_key_features_dict = [dict() for i in range(0, 3)]
        for j in range(1, 3):
            for s in range(0, len(self.backup_key_features[j])):
                word = self.backup_key_features[j][s]
                value = self.backup_key_features_count[j][s]
                self.backup_key_features_dict[j][word] = self.cluster_feature_dict[j][word] * value
                # print j, s, word, value, self.cluster_feature_dict[j][word], self.backup_key_features_dict[j][word]

        for j in range(1, 3):
            test = sorted(self.backup_key_features_dict[j].iteritems(), key=lambda d: d[1], reverse=True)
            if j == 2:
                count = 0
                for i in range(0, 10):
                    if test[i][0] not in self.max_frequent_feature:
                        self.max_frequent_feature.append(test[i][0])
                        count += 1
                        if count > 5:
                            break
            else:
                for i in range(0, 3):
                    if test[i][0] not in self.max_frequent_feature:
                        self.max_frequent_feature.append(test[i][0])

    # 针对特定特征做 正反 分析， 用于绘制雷达图
    def analyzekeyFeatures(self):
        feature_num = len(self.max_frequent_feature)
        print feature_num

        self.feature_count = []
        for i in range(0, feature_num):
            self.feature_count.append([0, 0, 0])
        for i in range(0, self.sentence_count):
            for j in range(0, feature_num):
                if self.max_frequent_feature[j] in self.batch_data_list[i]:
                    self.feature_count[j][self.batch_label_list[i]] += 1

        for i in range(0, feature_num):
            total = (self.feature_count[i][0] + self.feature_count[i][1] + self.feature_count[i][2]) / 10.0
            str_temp = '%s^%f^%f^%f,' % (
            self.max_frequent_feature[i], self.feature_count[i][0] / total, self.feature_count[i][1] / total,
            self.feature_count[i][2] / total)
            self.db_key_feature += str_temp
        self.db_key_feature = self.db_key_feature[:-1]
        # print self.db_key_feature

    # 将结果写入数据库
    def updataResults(self):
        sql = "insert into batch_results values (null, %s, '%s', '%s', '%s', '%s', '%s', '%s')" % (self.topic_id, self.topic_name, self.db_feature_set[0].encode('utf-8'), \
                                                                                         self.db_feature_set[1].encode('utf-8'),self.db_feature_set[2].encode('utf-8'), self.db_key_feature.encode('utf-8'), self.db_time_set)
        # print sql
        self.cursor.execute(sql)

        self.cursor.close()
        self.conn.commit()
        self.conn.close()

        for j in range(0, 3):
            file_path = '../../dataFolder/pre_topic_results/cluster_feature_dict_%d.csv' % j
            output_f = open(file_path, 'w')

            test = sorted(self.cluster_feature_dict[j].iteritems(), key=lambda d: d[1], reverse=True)
            max_frequent = test[0][1] / 110.0

            feature_count = 0
            for word, value in test:
                output_f.write('%s %f\n' % (word.encode('utf-8'), value / max_frequent))
                feature_count += 1
                if feature_count > 100:
                    break

            output_f.close()

        output_f = open('../../dataFolder/pre_topic_results/featuresAnalyze.csv', 'w')
        index = 0
        for i in range(0, len(self.max_frequent_feature)):
            total = (self.feature_count[i][0] + self.feature_count[i][1] + self.feature_count[i][2]) / 10.0
            output_f.write('%s %f %f %f\n' % (
            self.max_frequent_feature[i], self.feature_count[i][0] / total, self.feature_count[i][1] / total,
            self.feature_count[i][2] / total))
        output_f.close()


if __name__ == "__main__":
    batchAnalyze = BatchAnalyze(host='localhost', user='root', passwd='koche')
    batchAnalyze.analyzeBatchData(ur'xiaomi')
