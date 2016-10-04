# -*- coding: utf-8 -*-
import base64
import urllib
import time
import re
import json
import rsa
import binascii
import sys

from batching.weibo.weibo.items import WeiboItem

reload(sys)
sys.setdefaultencoding('utf8')

from lxml import etree
from bs4 import BeautifulSoup
from scrapy.http import Request
from scrapy.http import FormRequest

from scrapy.spiders import CrawlSpider


class CommentSpider(CrawlSpider):
    name = "comment"
    allowed_domains = ['weibo.com', 'sina.com.cn']

    __slots__ = ['keyword', 'start_page', 'end_page', 'username', 'password', 'topic_id']

    def __init__(self, keyword, topic_id, start_page=11, end_page=20,
                 username="18237363743", password="shanyong953", *a, **kw):
        super(CommentSpider, self).__init__(*a, **kw)
        self.keyword = keyword
        self.username = username
        self.password = password
        self.start_page = start_page
        self.end_page = end_page
        self.topic_id = topic_id

    # 输入用户名，发送请求，获得servertime,nonce,pubkey,rsakv以填充表单
    def start_requests(self):
        username = self.username
        print "username:%s" % username
        b64_text = urllib.quote(username)
        b64_text = base64.b64encode(bytearray(b64_text, 'utf-8'))
        b64_text = urllib.quote(b64_text)
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.11)&_=%s' % \
              (username, str(time.time()).replace('.', ''))
        return [Request(url=url, method='get', callback=self.post_message)]

    def post_message(self, response):
        p = re.compile('\((.*)\)')
        json_data = p.search(response.body).group(1)
        data = json.loads(json_data)
        servertime = data['servertime']
        nonce = data['nonce']
        publickey = data['pubkey']
        rsakv = data['rsakv']
        password = self.password
        # 密码加密
        pk = '0x' + publickey
        pk = int(pk, 16)
        key = rsa.PublicKey(pk, 65537)
        msg = str(servertime) + '\t' + str(nonce) + '\n' + password
        password = rsa.encrypt(msg, key)
        password = binascii.b2a_hex(password)
        request_body = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'useticket': '1',
            'pagerefer': 'http://login.sina.com.cn/sso/logout.php?entry=miniblog&r=http%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
            'vsnf': '1',
            'su': '',
            'service': 'miniblog',
            'servertime': '',
            'nonce': '',
            'pwencode': 'rsa2',
            'rsakv': '',
            'sp': '',
            'encoding': 'UTF-8',
            'prelt': '273',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META'
        }  # 表单可以自己查看是否需要改变
        request_body['sp'] = str(password)
        request_body['su'] = str(base64.b64encode("18237363743"))
        request_body['rsakv'] = rsakv
        request_body['nonce'] = nonce
        request_body['servertime'] = str(servertime)
        return [FormRequest(url='http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.4.11)',
                            formdata=request_body, callback=self.test)]  # 提交表单

    # 通过各种捕获地址，填充表单，发送post请求，此时登录成功，搜索rectcode如果为0，则证明登录成功，否则失败
    def test(self, response):
        data = response.body
        data = data[260:]
        p = re.compile('\((.*?)\)')
        json_data = p.search(data).group(1)
        p = json.loads(json_data)
        retcode = p["retcode"]
        if retcode == 0:
            start_pos = data.find('location.replace')
            end_pos = data.find('\');})')
            s = data[start_pos:end_pos]
            start_pos = s.find('http:')
            url = s[start_pos:]
            url = urllib.unquote(url)  # 跳转获取用户帐号的uniqueid以便登录帐号主页
        return [Request(url=url, method='get', callback=self.content_get)]

    def content_get(self, response):  # 获取主页
        data = response.body
        p = re.compile('\((.*)\)')
        json_data = p.search(data).group(1)
        json_data = json.loads(json_data)
        if (json_data['result']):
            json_data = json_data['userinfo']
            uniqueid = json_data['uniqueid']
            home_url = 'http://weibo.com/u/' + uniqueid + "/home"  # 进入帐号主页的url
        return [Request(url=home_url, method='get', callback=self.content_req)]

    # 构造搜索页面，keyword为关键词，page为搜索页面，不断yeild以获取不同的页面
    def content_req(self, response):
        keyword = self.keyword
        page = int(self.start_page)
        end = int(self.end_page)
        while page <= end:
            url = "http://s.weibo.com/weibo/" + keyword + "&page=" + str(page)
            page += 1
            yield Request(url=url, method='get', callback=self.parse_item)
            # 进入解析获取页面

    def parse_item(self, response):
        c = response.xpath("//script")
        d = len(c)
        # print str(d) + "weibo"这条语句用来检测是否成功，也可以不要
        if d > 21:  # 正常情况下d=25登陆过程中会出现两种情况，如果被ban它的d只有11个，则为失败，但是在少数情况下，它的页面也会出现d只有10个但是成功的情况，具体不知道，所有我用了if，else来获取全部正确，并没有设置错误检测
            q = c[21].extract()
            q = q.strip()
            e = len(q) - 10
            a = len('<script>STK && STK.pageletM && STK.pageletM.view(')
            wo = q[a:e]
            json_data = json.loads(wo)
            content = json_data['html']
            html = etree.HTML(content)
            divs = html.xpath(r'//div[@action-type="feed_list_item"]')
        else:
            html = etree.HTML(response.body)
            divs = html.xpath(r'//div[@action-type="feed_list_item"]')
        items = []
        # 开始分析
        for div in divs:
            content = div.xpath(r'.//div[@class="feed_content wbcon"]')[0]
            root = BeautifulSoup(etree.tostring(content, encoding="utf-8"), 'lxml')
            node = root.find('div')
            username = ""
            userid = ''
            userid = ''
            username = ''
            time = ''
            Content = ''
            from_ = ''
            zhuangfaliang = 0
            pinglun = 0
            zan = 0
            for children in node.children:
                if children.name == 'a':
                    if children.has_attr('usercard'):
                        e = children['usercard']
                        f = re.compile(r'\d+')
                        q = f.search(e)
                        b = q.group()
                        userid = b.strip()  # 用户的id
                    if children.has_attr('title'):
                        zhongjian = children["title"].strip()
                        username += zhongjian
                        # 用户名+认证类型，两种情况，两种获取的方式
                    else:
                        zhongjian = children.text.strip()
                        username += zhongjian
                if children.name == 'p':
                    Content = children.text.strip()  # 内容
            content = div.xpath(r'.//div[@class="feed_from W_textb"]')[0]
            root = BeautifulSoup(etree.tostring(content, encoding="utf-8"), 'lxml')
            node = root.find('div')
            for children in node.children:
                if children.name == 'a':
                    if children.has_attr('title'):
                        time = children["title"].strip()  # 发布时间
                    else:
                        from_ = children.text.strip()  # 来自什么途径发布
            content = div.xpath(r'.//div[@class="feed_action clearfix"]')[0]
            root = BeautifulSoup(etree.tostring(content, encoding="utf-8"), 'lxml')
            node = root.find('div')
            loop = 1
            for child in node.children:
                if child.name == 'ul':
                    for l in child.children:
                        if l.name == 'li':
                            for a in l:
                                if (loop == 2):
                                    zhuangfaliang = a.text.strip()  # 转发量
                                if (loop == 3):
                                    pinglun = a.text.strip()  # 评论量
                                if (loop == 4):
                                    zan = "赞" + a.text.strip()  # 赞数
                                loop += 1
            print from_

            item = WeiboItem()
            item['userID'] = userid
            item['userName'] = username
            item['time'] = time
            item['topicId'] = self.topic_id
            item['content'] = Content
            forward = re.match(r'转发(\d+)', zhuangfaliang)
            comment = re.match(r'评论(\d+)', pinglun)
            like = re.match(r'赞(\d+)', zan)
            if forward:
                item['forwardNum'] = forward.group(1)
            else:
                item['forwardNum'] = 0

            if comment:
                item['commentNum'] = comment.group(1)
            else:
                item['commentNum'] = 0

            if like:
                item['likeNum'] = like.group(1)
            else:
                item['likeNum'] = 0

            item.save()
            items.append(item)
            # # 略略提示下，我之前也是设过UTF-8按照网上教程在mysql里面，大部分都是中文没事，但还是会有一些例外乱码，你可以看看，二进制真心觉得是最简单的方法....
            # retstr = ''.join(map(lambda c: '%02x' % ord(c), text1))
            # retstr = "x'" + retstr + "'"
            # retstr1 = ''.join(map(lambda c: '%02x' % ord(c), text2))  # 为了解决MySQL的编码问题，统一以二进制的形式写入数据库
            # retstr1 = "x'" + retstr1 + "'"
            # retstr2 = ''.join(map(lambda c: '%02x' % ord(c), t))
            # retstr2 = "x'" + retstr2 + "'"
            # retstr3 = ''.join(map(lambda c: '%02x' % ord(c), text))
            # retstr3 = "x'" + retstr3 + "'"
            # retstr4 = ''.join(map(lambda c: '%02x' % ord(c), s))
            # retstr4 = "x'" + retstr4 + "'"
            # item['content'] = text2
            # item['title'] = text1
            # item['usercard'] = text
            # items.append(item)
        return items
