# -*- coding: utf-8 -*-
import re
import sys
import json

sys.path.append('/usr/bin/libsvm-3.21/python')
from svmutil import *


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv


class Judge:
    def __init__(self):
        # 获取疑问词库
        self.yiwen_corpus_list = self.getCorList('dataFolder/dict/corpus_yiwen.txt')
        self.yiwen_full_corpus_list = self.getCorList('dataFolder/dict/corpus_yiwen_full.txt')
        # 获取任指连词
        self.cc_corpus_list = self.getCorList('dataFolder/dict/corpus_cc.txt')
        # 获取正反疑问词
        self.zhengfan_corpus_list = self.getCorList('dataFolder/dict/corpus_zhengfan.txt')
        # 获取反问疑问词
        self.fanwen_corpus_list = self.getCorList('dataFolder/dict/corpus_fanwen.txt')
        # 标点
        self.biaodian_corpus_list = self.getCorList('dataFolder/dict/corpus_biaodian.txt')
        # 语气词
        self.yuqici_corpus_list = self.getCorList('dataFolder/dict/corpus_yuqici.txt')
        # 获取任指连词
        self.renzhi_corpus_list = self.getCorList('dataFolder/dict/corpus_renzhi.txt')
        # 获取假设连词
        self.jiashe_corpus_list = self.getCorList('dataFolder/dict/corpus_jiashe.txt')

        # 获取否定词库, 存放在列表neg_corpus_list中
        self.fouding_corpus_list = self.getCorList('dataFolder/dict/corpus_fouding.txt')
        self.fouding_full_corpus_list = self.getCorList('dataFolder/dict/corpus_fouding_full.txt')
        # self.neg_w_corpus_list = self.getCorList('dataFolder/dict/corpus_neg_weiyu.txt')
        # self.neg_z_corpus_list = self.getCorList('dataFolder/dict/corpus_neg_zhuanyu.txt')

        # 获取非否定的词
        self.unneg_corpus_list = self.getCorList('dataFolder/dict/corpus_unneg.txt')

        # 获取带比例的词典
        self.yiwen_front_corpus_list = self.getWeightCorList('dataFolder/dict_weight/yiwen_front_dict.csv')
        self.yiwen_after_corpus_list = self.getWeightCorList('dataFolder/dict_weight/yiwen_after_dict.csv')
        self.fouding_front_corpus_list = self.getWeightCorList('dataFolder/dict_weight/fouding_front_dict.csv')
        self.fouding_after_corpus_list = self.getWeightCorList('dataFolder/dict_weight/fouding_after_dict.csv')
        self.combine_yiwen_corpus_list = self.getWeightCorList('dataFolder/dict_weight/combine_yiwen_dict.csv')
        self.combine_fouding_corpus_list = self.getWeightCorList('dataFolder/dict_weight/combine_fouding_dict.csv')

        # 生成svm的向量 x是2维向量，每一维是每一个句子生成的向量，y是对应的标签
        self.y_vector = []
        self.x_vector = []

    # 从corpus_file中获取词库, 存放在corpus_list中
    def getCorList(self, corpus_file):
        corpus_list = []
        corpus_f = open(corpus_file)
        for temp_line in corpus_f:
            corpus_list.append(temp_line.strip())
        corpus_f.close()
        return corpus_list[:]

    # 从corpus_file中获取词库, 存放在corpus_list中
    def getWeightCorList(self, corpus_file):
        corpus_dict = {}
        corpus_f = open(corpus_file)
        cor_list = corpus_f.readlines()
        for cor_temp in cor_list:
            temp_sen_split_list = cor_temp.split(',')
            corpus_dict.setdefault(temp_sen_split_list[0], float(temp_sen_split_list[1]))
        corpus_f.close()
        return corpus_dict

    def replaceNoise(self, content):
        replace_factor1 = re.compile('//\w+\.\w+(\.\w+)*(/\w+)*', re.S)
        content = re.sub(replace_factor1, u'', content.decode('utf-8'))
        return content.encode('utf-8')

    # 读取训练数据
    def assignTrainDataList(self, input_file):
        print 'read train data'
        input_f = open(input_file)

        sen_list = input_f.readlines()
        for temp_sen in sen_list:
            temp_sen_split_list = temp_sen.split(' ', 1)
            self.train_label_list.append(temp_sen_split_list[0])
            self.train_data_list.append(temp_sen_split_list[1].strip())
        input_f.close()

    # 读取测试集
    def assignTestDataList(self, input_file):
        print 'read test data'
        input_f = open(input_file)
        sen_list = input_f.readlines()

        # 得到断句集最后一句的行号
        last_row_num = int(sen_list[-1].split('\t', 1)[0])

        # 存放每一行断句后的句子数
        self.test_sen_num_list = [0 for i in range(last_row_num)]

        for temp_sen in sen_list:
            temp_sen_split_list = temp_sen.split('\t', 1)
            temp_row_num = int(temp_sen_split_list[0]) - 1
            temp_sen_content = temp_sen_split_list[1].strip()
            self.test_data_list.append(temp_sen_content)
            self.test_sen_num_list[temp_row_num] += 1
            self.test_label_list.append('-1')
            self.test_data_keyfeatures_list.append([])
            # print '%d %s' % (temp_row_num,temp_sen_content)

        input_f.close()
        print u'获取断句集完毕'

    # 生成训练数据
    def generate_train_data(self):
        len_of_dataset = len(self.train_data_list)
        print 'the length of train data: %d' % len_of_dataset
        for i in range(0, len_of_dataset):
            # sen_unmark_content = self.train_unmark_list[i]
            # label_rule = self.classify(self.train_data_list[i],sen_unmark_content,i)
            # if label_rule == '-1':
            if 1:
                self.y_vector.append(float(self.train_label_list[i]))
                trainvector = self.get_vector(self.train_data_list[i], 1)
                self.x_vector.append(trainvector)
                self.svm_train_num += 1
        print ''
        print 'self.svm_train_num: %d' % self.svm_train_num

    # 对测试集生成svm的向量
    def generate_test_data(self):
        output_f = open('dataFolder/vector.txt', 'w')
        sen_index = 0
        len_of_dataset = len(self.test_sen_num_list)
        print 'the length of test data: %d' % len_of_dataset
        count = 0
        index = 0
        for sen_num in self.test_sen_num_list:
            # 显示已处理多少条
            if count % 10000 == 0:
                print '%d' % count
            count += 1
            # 存放该行所有断句的标签
            for sen_content in self.test_data_list[sen_index: sen_index + sen_num]:
                # testvector = self.get_vector(sen_content)
                sen_unmark_content = self.test_unmark_list[index]
                self.test_label_list[index] = self.classify(self.test_data_list[index], sen_unmark_content, index)
                if self.test_label_list[index] == '-1':
                    # self.test_label_list[index] = self.get_Label(sen_content, 0)
                    self.svm_test_index.append(index)
                    testvector = self.get_vector(sen_content, 0)
                    self.test_y_vector.append(-1.0)
                    self.test_x_vector.append(testvector)
                    output_f.write('%s\n' % testvector)
                index += 1
            sen_index += sen_num
        output_f.close()

    # 使用疑问词、否定词混合二元组判断
    def classify(self, seg_content, sen_unmark_content, seg_index):
        label_str = '-1'

        # empty
        if not seg_content:
            return '2'

        seg_content_list = seg_content.split(',')
        seg_content_length = len(seg_content_list)

        if seg_content_length == 1:
            if seg_content_list[0].decode('utf-8') == u'?x' or seg_content_list[0].decode('utf-8') == u'？x':
                return '2'

        ### 疑问句判断 ###
        # 初始判断
        is_renzhen_exist = 0
        is_jiashe_exist = 0
        is_buguan_exist = 0
        is_neg_exist = 0

        is_yuqici_exist = 0
        is_yiwenci_exist = 0
        is_yiwen_exsit = 0
        is_unnegword_exist = 0

        last_word = ''
        for i in range(0, seg_content_length):
            current_word = seg_content_list[i][:-1]
            current_flag = seg_content_list[i][-1]
            if current_flag != 'x':
                last_word = current_word
            if current_word in self.yiwen_corpus_list or current_word in self.yuqici_corpus_list or current_word in self.zhengfan_corpus_list:
                self.test_data_keyfeatures_list[seg_index].append([i, current_word, 0])
                is_yiwen_exsit = 1
            if current_word in self.unneg_corpus_list:
                self.test_data_keyfeatures_list[seg_index].append([i, current_word, 2])
                is_unnegword_exist = 1
            elif current_word in self.renzhi_corpus_list:
                self.test_data_keyfeatures_list[seg_index].append([i, current_word, 3])
                is_renzhen_exist = 1
            elif current_word in self.jiashe_corpus_list and i == 0:
                self.test_data_keyfeatures_list[seg_index].append([i, current_word, 4])
                is_jiashe_exist = 1
            elif current_word == '不管':
                self.test_data_keyfeatures_list[seg_index].append([i, current_word, 3])
                is_buguan_exist = 1
            elif current_word in self.fouding_corpus_list:
                self.test_data_keyfeatures_list[seg_index].append([i, current_word, 1])
                is_neg_exist = 1
            # 语气词、疑问词寻找
            elif current_word in self.yiwen_corpus_list:
                is_yiwenci_exist = 1
            elif current_word in self.yuqici_corpus_list:
                if i == seg_content_length - 1:
                    is_yuqici_exist = 1
                else:
                    for j in range(i + 1, seg_content_length):
                        if (not (seg_content_list[j][-1] == 'x' or seg_content_list[j][-1] == 'm')):
                            break
                    else:
                        is_yuqici_exist = 1
            # 反问句判断
            elif current_word in self.fanwen_corpus_list:
                return '2'
        # 含有否定假设或者任指型的词，不是否定句也不是疑问句
        if is_renzhen_exist == 1:
            return '2'
        # 以'不'结尾的疑问句
        if last_word == '不':
            return '0'
        if seg_content_length == 2 and is_yiwenci_exist == 0 and \
                (seg_content_list[seg_content_length - 1][:-1] == '?' or seg_content_list[seg_content_length - 1][
                                                                         :-1] == '？'):
            return '2'

        # 正反疑问句
        # 正反疑问句
        sen_unmark_content = self.replaceNoise(sen_unmark_content)

        for word in self.zhengfan_corpus_list:
            if word in sen_unmark_content and is_buguan_exist == 0:
                length_word = len(word)
                word_index = sen_unmark_content.index(word)
                left_sentence = sen_unmark_content[:word_index]
                # for fouding_word in self.fouding_full_corpus_list:
                #     if fouding_word in left_sentence:
                #         return '0'
                if word == '有木有':  # 有木有不能放于句末
                    r_index = length_word + word_index + 3
                    if r_index > len(sen_unmark_content):
                        r_index = len(sen_unmark_content)
                    after_char = sen_unmark_content[word_index + length_word:r_index].rstrip()
                    if after_char != '':
                        for biaodian in self.biaodian_corpus_list:
                            if biaodian in after_char and not ('?' in after_char or '？' in after_char):
                                label_str = '2'
                                return label_str
                                # return '3'
                    else:
                        if seg_content_list[0][:-1] == '有木有':
                            return '0'
                        else:
                            return '2'
                after_sentence = sen_unmark_content[word_index + length_word:].rstrip()
                if ' ' in after_sentence:
                    # 后面还有句子的，但句子不长的可以算做正反疑问句
                    after_e_sentence = after_sentence[after_sentence.index(' ') + 1:]
                    if len(after_e_sentence) <= 9:
                        label_str = '0'
                        return label_str
                else:
                    label_str = '0'
                    return label_str

        xuanze_index_l = -1
        xuanze_index_r = -1
        yinhao_index_l = -1
        yinhao_index_r = -1
        empty_index = -1
        shuminghao_index = -1

        for i in range(0, seg_content_length):
            current_word = seg_content_list[i][:-1]
            current_flag = seg_content_list[i][-1]
            # 选择疑问句
            if current_word == '是':
                xuanze_index_l = i
            elif current_word == ' ':
                empty_index = i
            elif current_word == '还是':
                xuanze_index_r = i
                if xuanze_index_r > xuanze_index_l and xuanze_index_l != -1 and is_renzhen_exist != 1 and \
                                empty_index < xuanze_index_l and is_buguan_exist == 0:
                    label_str = '0'
                    return label_str
            # 引号
            elif current_word == '“':
                yinhao_index_l = i
            elif current_word == '”':
                yinhao_index_r = i
            elif current_word == '：':
                maohao_index = i
            # 半书名号
            elif (current_word == '《') and i != 0 and i != seg_content_length - 1:
                shuminghao_index = i

            # elif current_word == '难道' and is_neg_exist == 1:
            #     return '2'

            # 是非问句 current_word == '吗' or current_word == '么' or current_word == '捏'
            if ('吗' in current_word or current_word == '么' or current_word == '捏') and '么么' not in sen_unmark_content:
                if i == seg_content_length - 1:
                    label_str = '0'
                    return label_str
                else:
                    for j in range(i + 1, seg_content_length):
                        # 一般疑问词在句首
                        if i == 0:
                            break
                        # 后面跟的是一个汉字的
                        if seg_content_list[j][-1] != 'x' and (j == seg_content_length - 1) and j == i + 1:
                            label_str = '0'
                            return label_str
                        # 从后面第二个词开始，有非标点符号的
                        if (not (seg_content_list[j][-1] == 'x' or seg_content_list[j][-1] == 'm')) and j != i + 1:
                            break
                        # 说话的
                        if yinhao_index_l != -1 and seg_content_list[j][:-1] == '”':
                            break
                    else:
                        label_str = '0'
                        return label_str
            elif current_word == '吧' or current_word == '啊':
                if i != seg_content_length - 1:
                    if seg_content_list[i + 1][:-1] == '?' or seg_content_list[i + 1][:-1] == '？':
                        label_str = '0'
                        return label_str

        if is_yuqici_exist == 1 and is_yiwenci_exist == 1 and shuminghao_index == -1:
            label_str = '0'
            return label_str

        # 包含假设性连词的可以为疑问句，但不能是否定句
        # if is_jiashe_exist == 1 and is_yiwen_exsit == 0 and is_neg_exist == 1:
        #     return '2'

        # 否定句判断
        if is_unnegword_exist == 1 or is_yiwen_exsit == 1:
            return '-1'

        # 读取pv和pv_modify
        pv_fouding_exist = 0
        pv_m_fouding_exist = 0
        pv_list = []
        pv_m_list = []
        len_pv_list = 0
        len_pv_m_list = 0
        neg_pv_count = 0
        neg_pv_m_count = 0
        neg_word_count = 0
        if 1:  # self.pv_index_list[seg_index] != '-1':
            pv_index = seg_index
            if self.pv_word_list[pv_index] != '':
                pv_list = self.pv_word_list[pv_index].split(' ')
                len_pv_list = len(pv_list)
            if self.pv_f_word_list[pv_index] != '':
                pv_m_list = self.pv_f_word_list[pv_index].split(' ')
                len_pv_m_list = len(pv_m_list)

        # 获取pv和pv_modify
        pv_neg_index = []
        if len_pv_list != 0:
            for i in range(0, len_pv_list):
                if pv_list[i] in self.fouding_corpus_list:
                    pv_fouding_exist = 1
                    neg_pv_count += 1
                    pv_neg_index.append(1)
                else:
                    pv_neg_index.append(0)
        if len_pv_m_list == 0:
            if pv_fouding_exist == 1:
                if neg_pv_count != 2:
                    label_str = '1'
                    return label_str
                else:
                    label_str = '2'
                    return label_str
        else:  # len_pv_m_list != 0
            if pv_fouding_exist == 0:
                pre_pv_word_index = -1
                for i in range(0, len_pv_m_list):
                    pv_modifier_word = pv_m_list[i][:-1]
                    pv_word_index = int(pv_m_list[i][-1])
                    if pre_pv_word_index != pv_word_index:
                        if pv_m_fouding_exist == 1:
                            if neg_pv_m_count != 2:
                                label_str = '1'
                                return label_str
                            else:
                                label_str = '2'
                                return label_str
                        pv_m_fouding_exist = 0
                        neg_pv_m_count = 0
                    if pv_modifier_word in self.fouding_corpus_list:
                        pv_m_fouding_exist = 1
                        neg_pv_m_count += 1
                    pre_pv_word_index = pv_word_index
                if pv_m_fouding_exist == 1:
                    if neg_pv_m_count != 2:
                        label_str = '1'
                        return label_str
                    else:
                        label_str = '2'
                        return label_str
            else:
                # 有否定谓语的，又可能有否定状语
                neg_word_count = neg_pv_count
                for i in range(0, len_pv_m_list):
                    pv_modifier_word = pv_m_list[i][:-1]
                    pv_word_index = int(pv_m_list[i][-1])

                    if pv_modifier_word in self.fouding_corpus_list:
                        if pv_neg_index[pv_word_index] == 0:
                            pv_m_fouding_exist = 1
                            neg_word_count += 1
                        else:
                            label_str = '2'
                            return label_str

                # 只有否定谓语的
                if pv_m_fouding_exist == 0 and is_yiwen_exsit != 1:
                    if neg_word_count != 2:
                        label_str = '1'
                        return label_str
                    else:
                        label_str = '2'
                        return label_str
                # 否定状语 不是修饰 否定谓语
                if pv_m_fouding_exist == 1 and is_yiwen_exsit != 1:
                    label_str = '1'
                    return label_str

        if neg_word_count == 2:
            return '2'

        return '-1'

    # 生成SVM向量
    def get_vector(self, seg_content, is_train):
        label_str = '2'
        trainvector = []

        # empty
        if not seg_content:
            for i in range(0, self.dimension_num):
                trainvector.append(0)
            return trainvector

        seg_content_list = seg_content.split(',')
        seg_content_length = len(seg_content_list)

        if seg_content_length == 1:
            if seg_content_list[0].decode('utf-8') == u'?x' or seg_content_list[0].decode('utf-8') == u'？x':
                for i in range(0, self.dimension_num):
                    trainvector.append(0)
                return trainvector

        # 变量
        neg_count = 0
        yiwen_f = 0
        yiwen_a = 0
        fouding_f = 0
        fouding_a = 0
        front_flag = '-'

        combine_yiwen = 0
        combine_fouding = 0
        combine_word = ''
        is_first_word = -1

        # 疑问词、否定词位置
        yiwen_index = 0
        fouding_index = 0

        for i in range(0, seg_content_length):
            current_word = seg_content_list[i][:-1]
            current_flag = seg_content_list[i][-1]

            # 前置词
            word_front_flag = current_word + front_flag

            # 疑问词前置判断
            if self.yiwen_front_corpus_list.get(word_front_flag, 0) > yiwen_f:
                yiwen_f = self.yiwen_front_corpus_list.get(word_front_flag, 0)
                yiwen_index = i + 1

            # 否定前置判断
            if self.fouding_front_corpus_list.get(word_front_flag, 0) > fouding_f:
                fouding_f = self.fouding_front_corpus_list.get(word_front_flag, 0)
                fouding_index = i + 1

            # 后词flag
            if i != seg_content_length - 1:
                after_flag = seg_content_list[i + 1][-1]
            else:
                after_flag = '-'

            # 后置词
            word_after_flag = current_word + after_flag

            # 疑问词后置判断
            if self.yiwen_after_corpus_list.get(word_after_flag, 0) > yiwen_a:
                yiwen_a = self.yiwen_after_corpus_list.get(word_after_flag, 0)
                yiwen_index = i + 1

            # 否定词后置判断
            if self.fouding_after_corpus_list.get(word_after_flag, 0) > fouding_a:
                fouding_a = self.fouding_after_corpus_list.get(word_after_flag, 0)
                fouding_index = i + 1

            if current_word in self.fouding_full_corpus_list:
                neg_count += 1

            if is_first_word == -1:
                if current_word in self.yiwen_corpus_list:
                    combine_word = current_word + '_'
                    is_first_word = 0
                elif current_word in self.fouding_corpus_list:
                    combine_word = current_word + '_'
                    is_first_word = 1
            elif is_first_word != -2:
                if (current_word in self.yiwen_corpus_list and is_first_word == 1) or (
                                current_word in self.fouding_corpus_list and is_first_word == 0):
                    combine_word += current_word
                    combine_yiwen = self.combine_yiwen_corpus_list.get(combine_word, 0)
                    combine_fouding = self.combine_fouding_corpus_list.get(combine_word, 0)
                    # if combine_yiwen!= 0 or combine_fouding != 0:
                    #     print combine_yiwen,combine_fouding
                    is_first_word = -2

            # 前词flag
            front_flag = current_flag
            front_word = current_word

        # 构造向量
        trainvector.append(yiwen_f)
        trainvector.append(yiwen_a)

        trainvector.append(fouding_f)
        trainvector.append(fouding_a)

        trainvector.append(combine_yiwen)
        trainvector.append(combine_fouding)

        # trainvector.append(seg_content_length)
        trainvector.append(neg_count)

        if yiwen_index > fouding_index:
            trainvector.append(1.0)
        else:
            trainvector.append(-1.0)

        # 疑问词、否定词哪个在前
        # trainvector.append(yiwen_index-fouding_index)

        # 我们预测的标签
        # trainvector.append(label_str)

        return trainvector

    # SVM 训练
    def svm_train(self):
        print '************  train  ************'
        self.model = svm_train(self.y_vector[:self.svm_train_num], self.x_vector[:self.svm_train_num], '-c 4 -g 0.07')

    def svm_test(self):
        print '************  test ************'
        p_label, p_acc, p_val = svm_predict(self.test_y_vector[:], self.test_x_vector[:], self.model)
        for i in range(0, len(p_label)):
            index = self.svm_test_index[i]
            self.test_label_list[index] = str(int(p_label[i]))

    def output_results(self):
        # ouput
        output_f1 = open('dataFolder/result.csv', 'w')
        index = 0
        for i in range(0, len(self.test_sen_num_list)):
            len_i = self.test_sen_num_list[i]
            for j in range(0, len_i):
                if j == len_i - 1:
                    output_f1.write('%s\n' % (self.test_label_list[index]))
                else:
                    output_f1.write('%s,' % (self.test_label_list[index]))
                index += 1
        output_f1.close()

        output_f2 = open('dataFolder/key_features.csv', 'w')

        sen_index = 0
        index = 0
        for sen_num in self.test_sen_num_list:
            for i in range(sen_index, sen_index + sen_num):
                temp_len = len(self.test_data_keyfeatures_list[i])
                if temp_len == 0:
                    output_f2.write('%d\n' % index)
                else:
                    output_f2.write('%d\t' % index)
                    for j in range(0, temp_len):
                        if j != temp_len - 1:
                            output_f2.write('%d:%d,' % (
                                self.test_data_keyfeatures_list[i][j][0], self.test_data_keyfeatures_list[i][j][2]))
                        else:
                            output_f2.write('%d:%d\n' % (
                                self.test_data_keyfeatures_list[i][j][0], self.test_data_keyfeatures_list[i][j][2]))

            sen_index += sen_num
            index += 1
        output_f2.close()
        return self.test_label_list[0]

        # output_f1 = open('dataFolder/result.csv', 'w')
        # index = 0
        # for i in range(0,len(self.test_sen_num_list)):

    # train
    def train(self, train_file='dataFolder/train/train.txt',
              train_numark_file='dataFolder/train/pre_train_duanju.csv',
              train_pv_file='dataFolder/train/train_pv_word.txt',
              train_pv_modifier_file='dataFolder/train/train_pv_modifier_word.txt'):
        # read data
        # 未处理文本
        input_f = open(train_numark_file)
        self.train_unmark_list = input_f.readlines()
        input_f.close()

        # 谓语中心语
        self.train_pv_word_list = self.getCorList(train_pv_file)
        self.train_pv_f_word_list = self.getCorList(train_pv_modifier_file)

        # 存训练集和测试集
        self.train_data_list = []
        # 存放训练集的标注
        self.train_label_list = []
        # 读取训练集
        self.assignTrainDataList(
            input_file=train_file
        )

        # 生成svm的向量的维度
        self.dimension_num = 8
        self.svm_train_num = 0

        self.generate_train_data()
        self.svm_train()

    # get PV words
    def get_PV(self, hgd_file, test_numark_file):
        input_f = open(hgd_file)
        input_f1 = open(test_numark_file)
        output_f1 = open('dataFolder/test/test_pv_word.txt', 'w')
        output_f2 = open('dataFolder/test/test_pv_modifier_word.txt', 'w')

        sentence_list = input_f1.readlines()

        total_sentence = 0
        for file_line in input_f:
            file_line_list = json.loads(file_line.strip(), object_hook=_decode_dict)
            for sentence in file_line_list:
                root_id = -1
                pv_id_list = []
                pv_modifier_id_list = []
                pv_word_list = []
                pv_modifier_word_list = []
                length = len(sentence[0])

                # 关键谓语
                for i in range(0, length):
                    if sentence[0][i]['parent'] == -1 and sentence[0][i]['pos'] != 'wp':
                        root_id = i
                        pv_id_list.append(root_id)
                        pv_word_list.append(sentence[0][i]['cont'])
                        # print '%s %s' % (sentence[0][i]['cont'],sentence[0][i]['semrelate'])

                # 并列谓语，宾语（动词）
                begin_index = 0
                end_index = len(pv_id_list)
                if sentence[0][root_id]['pos'] == 'v':
                    while 1:
                        for j in range(begin_index, end_index):
                            for i in range(0, length):
                                if sentence[0][i]['parent'] == pv_id_list[j] and (
                                                    sentence[0][i]['relate'] == 'COO' or sentence[0][i][
                                                'relate'] == 'CMP' or
                                                sentence[0][i]['relate'] == 'POB'):
                                    pv_word_list.append(sentence[0][i]['cont'])
                                    pv_id_list.append(i)
                        if end_index == len(pv_id_list):
                            break
                        else:
                            begin_index = end_index
                            end_index = len(pv_id_list)
                else:
                    while 1:
                        for j in range(begin_index, end_index):
                            for i in range(0, length):
                                if sentence[0][i]['parent'] == pv_id_list[j] and (
                                                    sentence[0][i]['relate'] == 'COO' or sentence[0][i][
                                                'relate'] == 'CMP' or
                                                sentence[0][i]['relate'] == 'POB'):
                                    pv_word_list.append(sentence[0][i]['cont'])
                                    pv_id_list.append(i)
                                # VOB：动宾关系
                                elif sentence[0][i]['parent'] == pv_id_list[j] and sentence[0][i][
                                    'relate'] == 'VOB' and (
                                                    sentence[0][i]['pos'] == 'v' or sentence[0][i]['pos'] == 'a' or
                                                sentence[0][i]['pos'] == 'n'):
                                    pv_word_list.append(sentence[0][i]['cont'])
                                    pv_id_list.append(i)
                                # ATT: 定中关系
                                elif sentence[0][i]['parent'] == pv_id_list[j] and sentence[0][i][
                                    'relate'] == 'ATT' and (
                                                sentence[0][i]['pos'] == 'v' or sentence[0][i]['pos'] == 'a'):
                                    pv_word_list.append(sentence[0][i]['cont'])
                                    pv_id_list.append(i)
                                # SBV：主谓关系
                                elif sentence[0][i]['parent'] == pv_id_list[j] and sentence[0][i][
                                    'relate'] == 'SBV' and (sentence[0][i]['pos'] == 'v'):
                                    pv_word_list.append(sentence[0][i]['cont'])
                                    pv_id_list.append(i)
                        if end_index == len(pv_id_list):
                            break
                        else:
                            begin_index = end_index
                            end_index = len(pv_id_list)

                # 首要状语
                for j in range(0, len(pv_id_list)):
                    for i in range(0, length):
                        if sentence[0][i]['parent'] == pv_id_list[j] and (
                                    sentence[0][i]['relate'] == 'ADV'):  # or sentence[0][i]['relate'] == 'ATT'
                            pv_modifier_word = sentence[0][i]['cont'] + str(j).encode('utf-8')
                            # print '%s %s\n' % (sentence[0][i]['cont'], pv_modifier_word)
                            pv_modifier_word_list.append(pv_modifier_word)
                            pv_modifier_id_list.append(i)

                # 修饰状语的状语
                begin_index = 0
                end_index = len(pv_modifier_id_list)
                while 1:
                    for j in range(begin_index, end_index):
                        for i in range(0, length):
                            if sentence[0][i]['parent'] == pv_modifier_id_list[j] and (
                                        sentence[0][i]['relate'] == 'ADV'):
                                pv_modifier_word = sentence[0][i]['cont'] + pv_modifier_word_list[j][-1]
                                # print '%s %s\n' % (sentence[0][i]['cont'], pv_modifier_word)
                                pv_modifier_word_list.append(pv_modifier_word)
                                pv_modifier_id_list.append(i)
                    if end_index == len(pv_modifier_id_list):
                        break
                    else:
                        begin_index = end_index
                        end_index = len(pv_modifier_id_list)

                # output data
                # if sentence[0][root_id]['pos'] != 'v':
                for pv_word in pv_word_list:
                    output_f1.write('%s ' % (pv_word))
                # output_f1.write('%s' % sentence_list[total_sentence].strip())
                output_f1.write('\n')

                for pv_modifier_word in pv_modifier_word_list:
                    # print '%s\n' % (pv_modifier_word)
                    output_f2.write('%s ' % (pv_modifier_word))
                # output_f2.write('%s' % sentence_list[total_sentence].strip())
                output_f2.write('\n')

                total_sentence += 1

                # print '\ncount:%d' % total_sentence

        input_f.close()
        input_f1.close()
        output_f1.close()
        output_f2.close()

    # test
    def test(self, test_numark_file='dataFolder/test/test_duanju.csv',
             test_file='dataFolder/test/test.txt',
             test_pv_file='dataFolder/test/test_pv_word.txt',
             test_pv_modifier_file='dataFolder/test/test_pv_modifier_word.txt'):
        # 读未处理句子
        input_f = open(test_numark_file)
        self.test_unmark_list = input_f.readlines()
        input_f.close()

        # 句法分析结果
        self.pv_word_list = self.getCorList(test_pv_file)
        self.pv_f_word_list = self.getCorList(test_pv_modifier_file)

        # 存测试集每一行的行号
        self.test_sen_num_list = []
        # 存测试集
        self.test_data_list = []
        self.test_data_keyfeatures_list = []
        # 存放测试集的标注
        self.test_label_list = []
        self.assignTestDataList(
            input_file=test_file
        )

        # 生成svm的向量 x是2维向量，每一维是每一个句子生成的向量，y是对应的标签
        self.test_x_vector = []
        self.test_y_vector = []
        self.svm_test_index = []

        self.generate_test_data()
        if len(self.test_x_vector) != 0:
            self.svm_test()
        return self.output_results()


if __name__ == "__main__":
    #     test_numark_file = 'dataFolder/train/pre_train_duanju.csv',
    #     test_file = 'dataFolder/train/pre_train_1232.txt',
    #     pv_file = 'dataFolder/hgd\train_pv_word.txt',
    #     pv_modifier_file = 'dataFolder/hgd\train_pv_modifier_word.txt',
    #     pv_index_file = 'dataFolder/hgd\train_pv_index.txt'

    # 生成判别模型，需在系统启动时就已经运行
    judge = Judge()
    judge.train(
        train_file='dataFolder/train/train.txt',
        train_numark_file='dataFolder/train/pre_train_duanju.csv',
        train_pv_file='dataFolder/train/train_pv_word.txt',
        train_pv_modifier_file='dataFolder/train/train_pv_modifier_word.txt')

    # 测试部分
    # 获取句子的谓语中心语和状语
    # hgd_file 是指经过哈工大预处理后的句子
    # test_numark_file 是指没有处理过的句子
    # judge.get_PV(
    #     hgd_file = 'dataFolder/test/test_ltp.txt',
    #     test_numark_file = 'dataFolder/test/test_duanju.csv')

    # hgd_file 是指经过哈工大预处理后的句子
    # test_numark_file 是指没有处理过的句子
    # test_file 是指分词后句子
    judge.test(
        test_numark_file='dataFolder/test/test_duanju.csv',
        test_file='dataFolder/test/test.txt',
        test_pv_file='dataFolder/test/test_pv_word.txt',
        test_pv_modifier_file='dataFolder/test/test_pv_modifier_word.txt')
    # judge.verify()
