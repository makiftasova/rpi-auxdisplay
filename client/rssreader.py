import threading
import feedparser
import json
import logging2

import utils


class RssReader(utils.LoopTask):
    __DATA_TYPE = 'news'

    def __init__(self, rss_url, display_client, num_of_news=10, interval=5,
                 group=None, name=None, args=(), kwargs=None, *, daemon=None):
        super(RssReader, self).__init__(interval=interval, group=group, name=name, args=args,
                                        daemon=daemon, kwargs=kwargs)
        self.url = rss_url
        self.display = display_client
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
