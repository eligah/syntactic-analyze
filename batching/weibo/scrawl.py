from twisted.internet import reactor

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from batching.weibo.weibo.spiders.comment import CommentSpider


def crawl(keyword, topic_id):
    configure_logging()
    runner = CrawlerRunner()
    runner.crawl(CommentSpider, keyword=keyword, topic_id=topic_id, start_page=0, end_page=9)
    runner.crawl(CommentSpider, keyword=keyword, topic_id=topic_id, start_page=10, end_page=19,
                 username='15736954465', password='zhangqiao322')
    runner.crawl(CommentSpider, keyword=keyword, topic_id=topic_id, start_page=20, end_page=29,
                 username='15962390142', password='lunzhi598')
    runner.crawl(CommentSpider, keyword=keyword, topic_id=topic_id, start_page=30, end_page=39,
                 username='17071584445', password='yikong145')
    d = runner.join()
    d.addBoth(lambda _: reactor.stop())

    reactor.run()  # the script will block here until all crawling jobs are finished
