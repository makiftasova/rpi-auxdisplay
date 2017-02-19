import socket
import logging
import socketserver
import threading

import tkinter as tk
from tkinter import ttk

from zeroconf import Zeroconf, ServiceInfo


class CustomTCPServer(socketserver.TCPServer):
    def __init__(self, server_address, request_handler_class, bind_and_activate=True, gui=None, logger=None):
        super().__init__(server_address, request_handler_class, bind_and_activate)
        self.gui = gui
        self.logger = logger


class ClientRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip().decode('UTF-8')
        self.server.logger.info("data received: " + data)

        if self.server.gui is not None:
            self.server.gui.sock_data = data
            self.server.gui.trigger_gui_update()


class MainWindow(tk.Tk):
    def __init__(self, ip=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', self.on_exit)

        self.sock_data = None

        self.logger = logging.getLogger(__name__)

        if ip is None:
            raise ValueError("Listen ip is None")

        self.socket_server = CustomTCPServer((ip, 0), ClientRequestHandler, gui=self, logger=self.logger)
        self.socket_thread = threading.Thread(target=self.socket_server.serve_forever)
        self.socket_thread.setDaemon(True)
        self.socket_thread.start()
        self.ip = self.socket_server.socket.getsockname()[0]
        self.port = self.socket_server.socket.getsockname()[1]
        self.logger.info("Listening on " + self.ip + ":" + str(self.port))

        self.zeroconf = Zeroconf()
        self.__setup_zeroconf()
        self.logger.info("Zeroconf service registered.")

        self.bind(sequence="<<SOCKET_EVENT>>", func=self.handle_gui_update)
        self.msg = tk.StringVar()
        self.message_box = ttk.Label(textvariable=self.msg)
        self.message_box.pack()

        self.btn_quit = ttk.Button(text="Quit", command=self.on_exit)
        self.btn_quit.pack()

    def trigger_gui_update(self):
        self.event_generate("<<SOCKET_EVENT>>")

    def handle_gui_update(self, event):
        self.msg.set(self.sock_data)
        self.logger.info("Data received: " + self.msg.get().strip())

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
                                         address=socket.inet_aton(self.ip), port=self.port, properties=service_desc)

        self.zeroconf.register_service(self.zeroconf_info)
