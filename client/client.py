import logging
import socket
import sys
import json

from time import sleep

from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf, ZeroconfServiceTypes

from netdiscovery import AuxDisplayListener
from rss_reader import RssReader


class UpdateType(object):
    CLOCK = 'clock'
    COMMAND = 'command'
    EMAIL = 'email'
    NEWS = 'news'
    STOCK = 'stock'
    WEATHER = 'weather'


class Client(object):
    def __init__(self, debug=False):
        self.logger = logging.getLogger(__name__)
        self.__setup_logging(debug)
        self.service_type = "_scpi-raw._tcp.local."
        self.zeroconf = Zeroconf()
        self.listener = AuxDisplayListener(client=self, type=self.service_type)
        self.browser = ServiceBrowser(self.zeroconf, self.service_type, self.listener)
        self.displays = []
        self.active_display = ""
        self.display_ip = "0.0.0.0"
        self.display_port = 0
        self.is_connected = False

    def __setup_logging(self, debug):
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=log_level)
        logging.getLogger('zeroconf').setLevel(log_level)

    def send_json(self, json: str):
        if not self.is_connected:
            self.connect()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.display_ip, self.display_port))
        len_sent = s.send(bytes(json, 'UTF-8'))
        s.close()
        return len_sent

    def add_display(self, name):
        if name not in self.displays:
            self.displays.append(name)

    def remove_display(self, name):
        if name in self.displays:
            self.displays.remove(name)
        if self.active_display == name:
            self.is_connected = False

    def __ask_display(self):
        for num, name in enumerate(self.displays):
            print(num + 1, " ", name)
        disp_id = int(input("select>")) - 1
        return disp_id

    def connect(self, display_id=None):
        if display_id is None:
            display_id = self.__ask_display()
        if 0 > display_id > len(self.displays):
            raise IndexError("Illegal display index")
        self.active_display = self.displays[display_id]
        self.__get_service_info()
        self.is_connected = True

    def __get_service_info(self):
        info = self.zeroconf.get_service_info(self.service_type, self.active_display)
        self.display_ip = socket.inet_ntoa(info.address)
        self.display_port = info.port

    def close(self):
        # TODO send close command
        self.zeroconf.close()


# TODO temp code for testing
def handle_command(cmd):
    cmd = cmd.lower()
    args = cmd.split(" ")
    data_type = args[0]
    json_str = ""
    if data_type == UpdateType.STOCK:
        json_str = json.dumps({'type': data_type, 'data': args[1:]})
    else:
        data = " ".join(args[1:])
        json_str = json.dumps({'type': data_type, 'data': data})

    return json_str


if __name__ == "__main__":
    debug = False
    if len(sys.argv) > 1:
        debug = sys.argv[1:] == ['--debug']
    client = Client(debug=debug)
    sleep(1)
    client.connect()
    rss_reader = RssReader('http://aa.com.tr/tr/rss/default?cat=guncel', client, interval=1/6)
    while True:
        x = input(">>>")
        if x == "quit":
            json_str = json.dumps({'type': UpdateType.COMMAND, 'data': 'quit'})
            client.send_json(json_str)
            client.close()
            break
        client.send_json(handle_command(x))
