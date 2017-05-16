import os
import pwd
import appdirs
import shutil
import logging
import socket
import sys
import json
import time

import tkinter as tk

from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf, ZeroconfServiceTypes

from netdiscovery import AuxDisplayListener
from rssreader import RssReader
from maildaemon import MailDaemon
from datetimedaemon import DateTimeDaemon
from weatherdaemon import WeatherDaemon
from exchangerates import ExchangeRatesDaemon

APP_NAME = 'rpi-auxdisplay'


class UpdateType(object):
    DATETIME = 'datetime'
    COMMAND = 'command'
    EMAIL = 'email'
    EXCHANGE = 'exchange'
    NEWS = 'news'
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
        self.display_id = -1
        self.active_display = ""
        self.display_ip = "0.0.0.0"
        self.display_port = 0
        self.is_connected = False
        self.win_root = None
        self.win_listbox = None

    def __setup_logging(self, debug):
        log_level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(level=log_level)
        logging.getLogger('zeroconf').setLevel(log_level)

    def send_json(self, json_str: str):
        if not self.is_connected:
            self.connect()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.display_ip, self.display_port))
        json_str += "\n"  # add newline to end of json string
        len_sent = s.send(bytes(json_str, 'UTF-8'))
        print("sent: ", len_sent, len(json_str), len_sent == len(json_str))
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

    def __display_select_callback(self):
        disp_id = self.win_listbox.curselection()
        if not disp_id:
            top = tk.Toplevel()
            top.title("Error")
            msg = tk.Message(top, text="You must pick a display from list")
            msg.pack()
            button = tk.Button(top, text="OK", command=top.destroy)
            button.pack()
        else:
            self.display_id = disp_id[0]
            self.win_root.destroy()
            self.win_root = None

    def __ask_display(self):
        self.win_root = tk.Tk()
        self.win_listbox = tk.Listbox(self.win_root, selectmode=tk.SINGLE)
        for item in self.displays:
            self.win_listbox.insert(tk.END, item)
        self.win_listbox.pack()

        btn_ok = tk.Button(self.win_root, text="SELECT DISPLAY",
                           command=self.__display_select_callback)
        btn_ok.pack()

        btn_quit = tk.Button(self.win_root, text="QUIT",
                             command=self.win_root.quit)
        btn_quit.pack()
        tk.mainloop()

        # for num, name in enumerate(self.displays):
        #     print(num + 1, " ", name)
        # disp_id = int(input("select>")) - 1
        # return disp_id

    def connect(self, display_id=None):
        if display_id is None:
            self.__ask_display()
        if 0 > self.display_id > len(self.displays):
            raise IndexError("Illegal display index")
        self.active_display = self.displays[self.display_id]
        self.__get_service_info()
        self.is_connected = True

    def __get_service_info(self):
        info = self.zeroconf.get_service_info(self.service_type, self.active_display)
        self.display_ip = socket.inet_ntoa(info.address)
        self.display_port = info.port

    def close(self):
        self.zeroconf.close()
        json_str = json.dumps({'type': UpdateType.COMMAND, 'data': 'quit'})
        self.send_json(json_str)


if __name__ == "__main__":
    debug = False
    if len(sys.argv) > 1:
        debug = sys.argv[1:] == ['--debug']

    username = pwd.getpwuid(os.getuid())[0]
    app_dirs = appdirs.AppDirs(appname=APP_NAME, appauthor=APP_NAME)
    config_dir = app_dirs.user_config_dir
    config_file = os.path.join(config_dir, 'config.json')

    if not os.path.isdir(config_dir):
        try:
            os.makedirs(config_dir)
        except OSError as e:
            sys.exit("Failed to create directory: {info}".format(info=e))

    if not os.path.isfile(config_file):
        try:
            shutil.copy(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),
                                                     'config.json')), config_file)
        except (OSError, IOError) as e:
            sys.exit("Failed to copy default config file: {info}".format(info=e))

    with open(config_file, 'r') as file:
        config = json.load(file)

    config_mail = config['config']['mail']
    imap_url = config_mail['url']
    imap_port = config_mail['port']
    mail_user = config_mail['username']
    mail_pwd = config_mail['password']
    print("IMAP data set, starting..")
    client = Client(debug=debug)
    time.sleep(1)
    client.connect()
    rss_reader = RssReader(client, 'http://aa.com.tr/tr/rss/default?cat=guncel')
    rss_reader.start()

    mail_daemon = MailDaemon(client, imap_url, imap_port, mail_user, mail_pwd)
    mail_daemon.start()

    datetime_daemon = DateTimeDaemon(client)
    datetime_daemon.start()

    config_weather = config['config']['weather']
    weather_daemon = WeatherDaemon(client, config=config_weather)
    weather_daemon.start()

    exchange_rates_daemon = ExchangeRatesDaemon(client)
    exchange_rates_daemon.start()

    while True:
        x = input(">>>")
        if x in ("quit", "exit"):
            qtime = time.time()
            rss_reader.cancel()
            mail_daemon.cancel()
            datetime_daemon.cancel()
            weather_daemon.cancel()
            exchange_rates_daemon.cancel()
            client.close()
            client.logger.info("time spent for quiting: " + str(time.time() - qtime) + " seconds")
            break
