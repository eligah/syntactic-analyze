# Syntactic Analysis Demo

## This is my SRP(student research project) project when I was a sophomore

## 基本介绍

- _主要语言_：python
- _爬虫_：scrapy
- _前端_：bootstrap, jquery，d3.js
- _后台_：django
- _数据库_：mysql

## 功能：

1. 单句模式：输入句子 -> 结巴分词 -> 调用哈工大语法分析获得token -> 绘制语法树 -> 反馈
2. 批处理模式： 输入词语 -> 爬取相关微博 -> 聚类处理，提取关键词 -> 绘制字云图，雷达图

## todo:

1. radar.js and cloud.js 提供一个接口： 可以传入csv数据 和 容器div的id. 前者方便接受后台传来的csv数据， 后者降低耦合性。

2. 单句： 展示分词结果，以及关键词。 调整位置
