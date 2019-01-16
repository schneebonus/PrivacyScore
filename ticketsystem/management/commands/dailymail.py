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
from ticketsystem.models import DailyNotificationSubscriber
from ticketsystem.models import State
from django.conf import settings
import bleach
import smtplib
from django.conf import settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Command(BaseCommand):
    help = 'Send a daily notification to the operators. Should be triggered by a cron job.'

    def handle(self, *args, **options):
        pending_emails = Mail.objects.all().filter(answered=False)
        subscribers = [sub.address for sub in DailyNotificationSubscriber.objects.all()]

        body = """Hello Operator,

here is your daily privacyscore notification.

Currently we have """ + str(len(pending_emails)) + """ incoming e-mails waiting for an answer:\n"""

        for pemail in pending_emails:
            body += "\t" + pemail.title + "\n"

        body += """
ToDo: n vulnerable results are about to be published in the next 24 hours.

ToDo: unsubscribe link without admin permissions.
"""

        if len(pending_emails) > 0:
            print("Sending the mail!")
            # ToDo: send email
            fromaddr = settings.EMAIL_USERNAME

            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['Subject'] = "PrivacyScore: Daily Notification"

            msg.attach(MIMEText(body, 'utf-8'))

            s = smtplib.SMTP_SSL(host=settings.EMAIL_SMTP_SERVER, port=settings.EMAIL_SMTP_PORT)
            s.login(fromaddr, settings.EMAIL_PASSWORD)

            for r in subscribers:
                toaddr = r
                msg['To'] = toaddr
                s.sendmail(fromaddr, toaddr, msg.as_string())
            s.quit()
        else:
            print("DailyMail nit required (nothing to do)")
