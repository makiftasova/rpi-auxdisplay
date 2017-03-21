import logging
import imaplib

import utils


class MailDaemon(utils.LoopTask):
    def __init__(self, display, imap_url, imap_port, user, password, interval=0.2):
        super(MailDaemon, self).__init__(interval=interval)

        self.logger = logging.getLogger(__name__)

        self.display = display
        self.ImapClient = imaplib.IMAP4_SSL(imap_url, imap_port)
        self.ImapClient.login(user=user, password=password)
        self.ImapClient.select('INBOX')

    def loop(self):
        status, response = self.ImapClient.search(None, 'UNSEEN')
        unread_msg_nums = response[0].split()

        self.logger.info("# on unread mails: {}".format(len(unread_msg_nums)))

    def on_cancel(self):
        self.ImapClient.logout()
