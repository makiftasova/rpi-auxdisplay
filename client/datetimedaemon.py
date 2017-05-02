import datetime
import json
import logging

import utils


class DateTimeDaemon(utils.LoopTask):
    __DATA_TYPE = 'datetime'

    def __init__(self, display, interval=1):
        super(DateTimeDaemon, self).__init__(interval=interval, name="datetimedaemon-thread")
        self.display = display
        self.logger = logging.getLogger(__name__)

    def loop(self):
        dt_now = datetime.datetime.now()

        datetime_info = {'date': dt_now.strftime("%Y %m %d"), 'time': dt_now.strftime("%H:%M")}

        json_str = json.dumps({'type': self.__DATA_TYPE, 'data': datetime_info})
        self.display.send_json(json_str)
        self.logger.info("datetime pushed to display")
