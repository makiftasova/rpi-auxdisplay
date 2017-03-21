import logging
import imaplib
import json

import utils


class MailDaemon(utils.LoopTask):
    __DATA_TYPE = 'email'

    def __init__(self, display, imap_url, imap_port, user, password, interval=10):
        super(MailDaemon, self).__init__(interval=interval, name="maildaemon-thread")

        self.logger = logging.getLogger(__name__)

        self.display = display
        self.ImapClient = imaplib.IMAP4_SSL(imap_url, imap_port)
        self.ImapClient.login(user=user, password=password)
        self.ImapClient.select('INBOX')

    def loop(self):
        status, response = self.ImapClient.search(None, 'UNSEEN')
        unread_list = response[0].split()
        unread_num = len(unread_list)
        json_str = json.dumps({'type': self.__DATA_TYPE, 'data': unread_num})
        self.display.send_json(json_str)
        self.logger.info("unread mail count pushed to the display")

    def on_cancel(self):
        self.ImapClient.logout()
