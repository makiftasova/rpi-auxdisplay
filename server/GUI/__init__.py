import socket
import logging
import socketserver
import threading
import json

import tkinter as tk
from tkinter import ttk

from zeroconf import Zeroconf, ServiceInfo

from .widgets import *

__all__ = ["widgets"]


class UpdateType(object):
    CLOCK = 'clock'
    COMMAND = 'command'
    EMAIL = 'email'
    NEWS = 'news'
    STOCK = 'stock'
    WEATHER = 'weather'


class CustomTCPServer(socketserver.TCPServer):
    def __init__(self, server_address, request_handler_class, bind_and_activate=True, gui=None,
                 logger=None):
        super().__init__(server_address, request_handler_class, bind_and_activate)
        self.gui = gui
        self.logger = logger


class ClientRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        _data_file = self.request.makefile()
        data = _data_file.readline()
        # data = self.request.recv(4096).strip().decode('UTF-8')
        self.server.logger.info("data received: " + data)

        if self.server.gui is not None:
            data = json.loads(data)
            data_type = data['type']
            text = data['data']
            self.server.gui.sock_data = text
            self.server.gui.trigger_gui_update(data_type)


class MainWindow(tk.Tk):
    __EVENT_CLOCK_UPDATE = "<<UPDATE_CLOCK_EVENT>>"
    __EVENT_COMMAND_UPDATE = "<<UPDATE_COMMAND_EVENT>>"
    __EVENT_EMAIL_UPDATE = "<<UPDATE_EMAIL_EVENT>>"
    __EVENT_NEWS_UPDATE = "<<UPDATE_NEWS_EVENT>>"
    __EVENT_STOCK_UPDATE = "<<UPDATE_STOCK_EVENT>>"
    __EVENT_WEATHER_UPDATE = "<<UPDATE_WEATHER_EVENT>>"

    def __init__(self, ip=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', self.on_exit)

        self.resizable(width=False, height=False)
        self.geometry('{w}x{h}+{x}+{y}'.format(w=800, h=480, x=0, y=0))
        self.overrideredirect(True)  # disable title bar etc.

        self.sock_data = None

        self.logger = logging.getLogger(__name__)

        if ip is None:
            raise ValueError("Listen ip is None")

        self.socket_server = CustomTCPServer((ip, 0), ClientRequestHandler, gui=self,
                                             logger=self.logger)
        self.socket_thread = threading.Thread(target=self.socket_server.serve_forever)
        self.socket_thread.setDaemon(True)
        self.socket_thread.start()
        self.ip = self.socket_server.socket.getsockname()[0]
        self.port = self.socket_server.socket.getsockname()[1]
        self.logger.info("Listening on " + self.ip + ":" + str(self.port))

        self.zeroconf = Zeroconf()
        self.__setup_zeroconf()
        self.logger.info("Zeroconf service registered.")

        self.bind(sequence=self.__EVENT_CLOCK_UPDATE, func=self.handle_clock_update)
        self.bind(sequence=self.__EVENT_COMMAND_UPDATE, func=self.handle_command_update)
        self.bind(sequence=self.__EVENT_EMAIL_UPDATE, func=self.handle_email_update)
        self.bind(sequence=self.__EVENT_NEWS_UPDATE, func=self.handle_news_update)
        self.bind(sequence=self.__EVENT_STOCK_UPDATE, func=self.handle_stock_update)
        self.bind(sequence=self.__EVENT_WEATHER_UPDATE, func=self.handle_weather_update)

        self.news_label = None
        self.stock_label = None
        self.btn_quit = None
        self.after(10, self.__init_widgets__)

    def __init_widgets__(self):
        self.news_label = SlidingLabel(master=self, text_length=25)
        # self.news_label.grid(row=0, sticky=tk.W)
        self.news_label.pack(fill=tk.X)

        self.news_label.load_lines(["Breaking News"])

        self.stock_label = SlidingLabel(master=self, separator="|", text_length=25)
        # self.stock_label.grid(row=1, sticky=tk.W)
        self.stock_label.pack(after=self.news_label, fill=tk.X)

        self.stock_label.load_lines(["Exchange Rates"])

        self.btn_quit = ttk.Button(text="Quit", command=self.on_exit)
        # self.btn_quit.grid(row=2, sticky=tk.W)
        self.btn_quit.pack()

    def trigger_gui_update(self, data_type):
        if data_type == UpdateType.CLOCK:
            self.event_generate(self.__EVENT_CLOCK_UPDATE)
        elif data_type == UpdateType.COMMAND:
            self.event_generate(self.__EVENT_COMMAND_UPDATE)
        elif data_type == UpdateType.EMAIL:
            self.event_generate(self.__EVENT_EMAIL_UPDATE)
        elif data_type == UpdateType.NEWS:
            self.event_generate(self.__EVENT_NEWS_UPDATE)
        elif data_type == UpdateType.STOCK:
            self.event_generate(self.__EVENT_STOCK_UPDATE)
        elif data_type == UpdateType.WEATHER:
            self.event_generate(self.__EVENT_WEATHER_UPDATE)
        else:
            self.logger.error("Unknown data type: " + data_type)

    def handle_clock_update(self, event):
        pass

    def handle_command_update(self, event):
        cmd = self.sock_data
        if 'quit' == cmd:
            self.on_exit()

    def handle_email_update(self, event):
        pass

    def handle_news_update(self, event):
        self.news_label.load_lines(self.sock_data)

    def handle_stock_update(self, event):
        self.stock_label.load_lines(self.sock_data)
        pass

    def handle_weather_update(self, event):
        pass

    def on_exit(self):
        self.logger.info("Unregistering Zeroconf services...")
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()

        self.logger.info("Closing socket...")
        self.socket_server.socket.shutdown(socket.SHUT_RDWR)
        self.socket_server.socket.close()

        self.logger.info("Exiting...")
        self.destroy()

    def __setup_zeroconf(self):
        service_desc = {}

        self.zeroconf_info = ServiceInfo("_scpi-raw._tcp.local.",
                                         "Auxiliary Display on {host}._scpi-raw._tcp.local.".format(
                                             host=socket.gethostname()),
                                         address=socket.inet_aton(self.ip), port=self.port,
                                         properties=service_desc)

        self.zeroconf.register_service(self.zeroconf_info)
