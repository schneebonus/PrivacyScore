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
from django.conf import settings
import bleach

class Command(BaseCommand):
    help = 'Check for new emails and put them into the database. Should be triggered by a cron job.'

    def handle(self, *args, **options):
        imap_server = settings.EMAIL_IMAP_SERVER
        imap_port = settings.EMAIL_IMAP_PORT
        M = imaplib.IMAP4_SSL(imap_server, imap_port)
        try:
            M.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            M.select("INBOX", True)
            tmp, data = M.search(None, 'ALL')
            newest_known_email = Mail.objects.all().order_by('sequence').last()
            if newest_known_email is not None:
                highest_known_email = newest_known_email.sequence
            else:
                highest_known_email = 0
            for num in data[0].split():
                if int(num) > highest_known_email:
                    tmp, content = M.fetch(num, '(RFC822)')
                    msg = email.message_from_string(content[0][1].decode('utf-8'))
                    title = msg["Subject"]
                    direction = False
                    sequence = num
                    sender = msg["From"]
                    receiver = msg["To"]
                    # body = bleach.clean(msg.get_payload())
                    body = msg.get_payload()
                    received_at = msg["Date"]
                    url = ""

                    print(title + " from " + sender)

                    regex_url = "^.*Schwachstellen auf Ihrer Webseite \( (.*\..*) \).*$"
                    matchObj = re.match( regex_url, title)
                    if matchObj is not None:
                        url = matchObj.group(1)
                        issues = Issue.objects.all().filter(url=url)
                        for issue in issues:
                            state = State.objects.get(id=4)
                            history = HistoryElement(state=state, issue=issue)
                            history.save()

                    new_mail = Mail(title=title, direction=direction, sequence=sequence, sender=sender, receiver=receiver, body=body, url=url)
                    new_mail.save()

            M.close()
            M.logout()
        except imaplib.IMAP4.error:
            print("LOGIN FAILED!!!")
