import os
import datetime
import collections
import logging
import json
import urllib.request as urlrequest
import urllib.error as urlerror
import xml.etree.ElementTree as xmlparse

import utils


class ExchangeRatesTCMB(object):
    def __init__(self):
        self.base_url = "http://www.tcmb.gov.tr/kurlar/{year_month}/{day_month_year}.xml"
        self.data_file = ""
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        urlrequest.urlcleanup()

    def __create_url(self, day_offset=0):
        now = datetime.datetime.now()

        if day_offset != 0:
            time_diff = datetime.timedelta(days=day_offset)
            now += time_diff

        return self.base_url.format(year_month=now.strftime("%Y%m"),
                                    day_month_year=now.strftime("%d%m%Y"))

    def __find_most_recent_file(self):

        valid_data_found = False
        day_offset = 0
        data = None
        while True:
            url = self.__create_url(day_offset=day_offset)
            file = url.split('/')[-1]
            try:
                local_filename, headers = urlrequest.urlretrieve(url, file)
                self.data_file = local_filename
                break
            except urlerror.HTTPError as error:
                self.logger.info("URL: {url} Request failed with code: {code}".format(url=url, code=
                error.code))
                day_offset -= 1
                continue

    def get_rates(self):
        self.__find_most_recent_file()
        currency_dict = {}
        data = xmlparse.parse(self.data_file).getroot()
        for currency in data:
            code = currency.get('CurrencyCode')
            value = currency.findtext("BanknoteSelling")
            if value is not '':
                currency_dict.setdefault(code, value)
        os.remove(self.data_file)
        currency_dict = collections.OrderedDict(sorted(currency_dict.items()))
        return currency_dict


class ExchangeRatesDaemon(utils.LoopTask):
    __DATA_TYPE = 'exchange'

    def __init__(self, display, interval=5):
        super(ExchangeRatesDaemon, self).__init__(interval=interval,
                                                  name="exchangeratesdaemon-thread")
        self.display = display
        self.logger = logging.getLogger(__name__)

        self.rates = ExchangeRatesTCMB()

    def loop(self):
        current_rates = self.rates.get_rates()
        rate_list = []
        for key in current_rates:
            rate_list.append("{currency}: {rate}".format(currency=key, rate=current_rates[key]))
        json_str = json.dumps({'type': self.__DATA_TYPE, 'data': rate_list})
        self.display.send_json(json_str)
        self.logger.info("exchange rates pushed to display")
