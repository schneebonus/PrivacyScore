from django.core.management.base import BaseCommand, CommandError
import sys
import imaplib
import getpass
import email
import re
import datetime
from ticketsystem.models import Mail
from ticketsystem.models import Issue
from ticketsystem.models import HistoryElement
from ticketsystem.models import State
import chardet
from email.header import decode_header
from ticketsystem.models import Attachment
from django.conf import settings
import bleach
from imbox import Imbox
import email.parser


class Command(BaseCommand):
    help = 'Check for new emails and put them into the database. Should be triggered by a cron job.'

    def handle(self, *args, **options):
        imap_server = settings.EMAIL_IMAP_SERVER
        imap_port = settings.EMAIL_IMAP_PORT
        try:
            with Imbox(settings.EMAIL_IMAP_SERVER,
                       username=settings.EMAIL_USERNAME,
                       password=settings.EMAIL_PASSWORD,
                       ssl=True,
                       ssl_context=None,
                       starttls=False) as imbox:

                all_inbox_messages = imbox.messages()
                print(len(all_inbox_messages))
                for uid, message in all_inbox_messages:
                    print(message.message_id)
                    print("Subject:", message.subject)
                    print("Body:")
                    for m in message.body['plain']:
                        print(m)
        except imaplib.IMAP4.error:
            print("LOGIN FAILED!!!")
