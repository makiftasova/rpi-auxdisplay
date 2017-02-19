from zeroconf import Zeroconf, ServiceBrowser


class AuxDisplayListener(object):
    def __init__(self, client, type):
        self.client = client

    def remove_service(self, zeroconf, type, name):
        if name.startswith("Auxiliary Display on"):
            self.client.remove_display(name)

    def add_service(self, zeroconf, type, name):
        if name.startswith("Auxiliary Display on"):
            self.client.add_display(name)