import feedparser
import json
import logging

import utils


class RssReader(utils.LoopTask):
    __DATA_TYPE = 'news'

    def __init__(self, display, rss_url, num_of_news=10, interval=5):
        super(RssReader, self).__init__(interval=interval, name="rssreader-thread")
        self.url = rss_url
        self.display = display
        self.num_of_news = num_of_news
        self.logger = logging.getLogger(__name__)

    def loop(self):
        feed = feedparser.parse(self.url)
        headlines = feed.entries[self.num_of_news:]
        titles = []
        for news in headlines:
            titles.append(news.title)

        json_str = json.dumps({'type': self.__DATA_TYPE, 'data': titles})
        self.display.send_json(json_str)
        self.logger.info("rss feed pushed to display")
