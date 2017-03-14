import threading
import feedparser
import json

from time import sleep


class RssReader(threading.Thread):
    __DATA_TYPE = 'news'

    def __init__(self, rss_url, display_client, num_of_news=10, interval=5, group=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        super(RssReader, self).__init__(group=group, name=name, args=args, daemon=daemon,
                                        kwargs=kwargs)
        self.url = rss_url
        self.display = display_client
        self.loop = True
        self.num_of_news = num_of_news
        self.refresh_interval = int(interval * 60)

    def run(self):
        while (self.loop):
            feed = feedparser.parse(self.url)
            headlines = feed.entries[self.num_of_news:]
            titles = []
            for news in headlines:
                titles.append(news.title)

            json_str = json.dumps({'type': self.__DATA_TYPE, 'data': titles})
            self.display.send_json(json_str)
            print("rss feed pushed to display")
            sleep(self.refresh_interval)
        return

    def cancel(self):
        self.loop = False
