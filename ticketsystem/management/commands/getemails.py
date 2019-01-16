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
from ticketsystem.models import Attachment
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
                        try:
                            body = body_raw.decode('utf-8')
                        except UnicodeDecodeError:
                            body = body_raw.decode('iso-8859-1')
                        msg = email.message_from_string(body)
                        title = msg["Subject"]
                        direction = False
                        sequence = num
                        sender = msg["From"]
                        receiver = msg["To"]
                        body = ""
                        attachments = []
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain" or part.get_content_type() == "application/pgp-signature":
                                body += str(part.get_payload()) + "\n"
                            filename = part.get_filename()
                            if filename is not None:
                                attachments.append(filename)
                        received_at = msg["Date"]
                        url = ""

                        print(title + " from " + sender)


                        regex_url = "^.*Schwachstellen auf Ihrer Webseite \( (.*\..*) \).*$"
                        matchObj = re.match(regex_url, title)
                        if matchObj is not None:
                            url = matchObj.group(1)
                            issues = Issue.objects.all().filter(url=url)
                            for issue in issues:
                                state = State.objects.get(id=4)
                                history = HistoryElement(state=state, issue=issue)
                                history.save()

                        new_mail = Mail(title=title, direction=direction, sequence=sequence,
                                        sender=sender, receiver=receiver, body=body, url=url)
                        new_mail.save()

                        # attachments for email
                        for at in attachments:
                            att_model = Attachment(filename=at, mail = new_mail)
                            att_model.save()

                    except:
                        print("ERROR: Problem while handling this email: " + str(num))

            M.close()
            M.logout()
        except imaplib.IMAP4.error:
            print("LOGIN FAILED!!!")
