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

    def decode_sender(self, text):
        s, encoding = decode_header(text)[0]
        sender = s if type(s) is str else s.decode(
            encoding or 'utf-8')

        regex_url = "^.*<(.*)>*$"
        matchObj = re.match(regex_url, sender)
        if matchObj is not None:
            email = matchObj.group(1)
            return sender
        else:
            matchObj = re.match(regex_url, text)
            email = ""
            if matchObj is not None:
                email = matchObj.group(1)

            return sender + " <" + email + ">"

    def extract_uid(self, responce):
        responce_utf8 = responce[0].decode("utf-8")
        # Example: 5 (UID 38)
        regex_uid = "^.*\(UID (.*)\)>*$"
        matchObj = re.match(regex_uid, responce_utf8)
        if matchObj is not None:
            uid = matchObj.group(1)
            return uid
        return 0


    def handle(self, *args, **options):
        imap_server = settings.EMAIL_IMAP_SERVER
        imap_port = settings.EMAIL_IMAP_PORT
        M = imaplib.IMAP4_SSL(imap_server, imap_port)

        try:
            M.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            print("Login: OK")
            M.select("INBOX", False)
            tmp, data = M.search(None, 'ALL')
            known_uids = {int(email.sequence) for email in Mail.objects.all()}

            print("UIDs known by the ticketsystem:")
            print(known_uids)

            for num in data[0].split():
                tmp, uid = M.fetch(num, '(UID)')
                uid = self.extract_uid(uid)
                if int(uid) not in known_uids:
                    try:
                        tmp, content_raw = M.fetch(num, '(UID RFC822)')
                        body_raw = content_raw[0][1]

                        msg = email.message_from_bytes(content_raw[0][1])

                        # decode headers
                        s, encoding = decode_header(msg['Subject'])[0]
                        title = s if type(s) is str else s.decode(
                            encoding or 'utf-8')

                        print(title)

                        sender = self.decode_sender(msg['From'])

                        s, encoding = decode_header(msg['To'])[0]
                        receiver = s if type(s) is str else s.decode(
                            encoding or 'utf-8')

                        body = body_raw.decode(encoding or 'utf-8')
                        message_id = msg.get('Message-ID')
                        references = msg.get("References")
                        if references == None:
                            references = ""
                        direction = False
                        sequence = uid
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
                        else:
                            # regex did not get it (subject changed or spam)
                            # lets try to find the original mail in the headers
                            for ref in references.split(" "):
                                try:
                                    referencing_mail = Mail.objects.all().filter(message_id=ref)
                                    if len(referencing_mail) > 0:
                                        url = referencing_mail[0].url
                                except Mail.DoesNotExist:
                                    pass
                        if url != "":
                            issues = Issue.objects.all().filter(url=url)
                            print("\treply for: ", url)
                            for issue in issues:
                                state = State.objects.get(id=4)
                                history = HistoryElement(
                                    operator="Mail Cronjob",state=state, issue=issue)
                                history.save()

                        new_mail = Mail(title=title, direction=direction, sequence=sequence,
                                        sender=sender, receiver=receiver, body=body, url=url, message_id=message_id, references=references)
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
