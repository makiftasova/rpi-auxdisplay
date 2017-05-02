import requests
import json
import logging

import utils


class WeatherDaemon(utils.LoopTask):
    __DATA_TYPE = 'weather'

    def __init__(self, display, config={}, interval=15, request_timeout=5):
        super(WeatherDaemon, self).__init__(interval=interval, name="weatherdaemon-thread")

        self.display = display
        self.logger = logging.getLogger(__name__)
        self.timeout = request_timeout
        self.api_url = config['url']
        self.api_key = config['wunderground_key']
        self.country = config['country']
        self.city = config['city']
        self.request_url = self.api_url.format(api_key=self.api_key, country=self.country,
                                               city=self.city)

    def loop(self):
        r = requests.get(self.request_url, timeout=self.timeout)
        curr_observation = r.text['current_observation"']

        weather_data = {'temp': curr_observation['temp_c'], 'temp_unit':"C"}

        json_str = json.dumps({'type': self.__DATA_TYPE, 'data': weather_data})
        self.display.send_json(json_str)
        self.logger.info("datetime pushed to display")
