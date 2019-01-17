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
import email.parser


class Command(BaseCommand):
    help = 'Check for new emails and put them into the database. Should be triggered by a cron job.'

    def handle(self, *args, **options):
        imap_server = settings.EMAIL_IMAP_SERVER
        imap_port = settings.EMAIL_IMAP_PORT
        M = imaplib.IMAP4_SSL(imap_server, imap_port)
        try:
            M.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            print("Login: OK")
            M.select("INBOX", False)
            tmp, data = M.search(None, 'ALL')
            newest_known_email = Mail.objects.all().order_by('sequence').last()
            if newest_known_email is not None:
                highest_known_email = newest_known_email.sequence
            else:
                highest_known_email = 0
            print("newest_known_email = ", highest_known_email)
            print("Server has: " + str(data[0].split()))
            for num in data[0].split():
                if int(num) > highest_known_email:
                    try:
                        tmp, content_raw = M.fetch(num, '(RFC822)')
                        body_raw = content_raw[0][1]

                        msg = email.message_from_bytes(content_raw[0][1])

                        # decode headers
                        s, encoding = decode_header(msg['Subject'])[0]
                        title = s if type(s) is str else s.decode(
                            encoding or 'utf-8')

                        s, encoding = decode_header(msg['From'])[0]
                        sender = s if type(s) is str else s.decode(
                            encoding or 'utf-8')

                        s, encoding = decode_header(msg['To'])[0]
                        receiver = s if type(s) is str else s.decode(
                            encoding or 'utf-8')

                        body = body_raw.decode(encoding or 'utf-8')
                        message_id = msg.get('Message-ID')

                        direction = False
                        sequence = num
                        body = ""
                        attachments = []
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain" or part.get_content_type() == "application/pgp-signature":
                                payload_raw = part.get_payload(decode=True)
                                payload = payload_raw.decode(part.get_content_charset() or "utf-8")

                                body += payload + "\n"
                            filename = part.get_filename()
                            if filename is not None:
                                attachments.append(filename)
                        received_at = msg["Date"]
                        url = ""

                        regex_url = "^.*Schwachstellen auf Ihrer Webseite \( (.*\..*) \).*$"
                        matchObj = re.match(regex_url, title)
                        if matchObj is not None:
                            url = matchObj.group(1)
                            issues = Issue.objects.all().filter(url=url)
                            for issue in issues:
                                state = State.objects.get(id=4)
                                history = HistoryElement(
                                    state=state, issue=issue)
                                history.save()
                        new_mail = Mail(title=title, direction=direction, sequence=sequence,
                                        sender=sender, receiver=receiver, body=body, url=url, message_id=message_id)
                        new_mail.save()

                        # attachments for email
                        for at in attachments:
                            att_model = Attachment(filename=at, mail=new_mail)
                            att_model.save()
                    except Exception as e:
                        print("ERROR: Problem while handling this email: " + str(num))
                        print(e)

            M.close()
            M.logout()
        except imaplib.IMAP4.error:
            print("LOGIN FAILED!!!")
