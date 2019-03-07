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
# import bleach
import smtplib
from django.conf import settings
import pytz
from datetime import datetime, timedelta

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Command(BaseCommand):
    help = 'Send a daily notification to the operators. Should be triggered by a cron job.'

    def next_publications(self):
        now = datetime.now(pytz.utc)
        next_7_days = timedelta(days=7)
        notify_until = now + next_7_days
        next_publications = Issue.objects.all().filter(
            publication__gte=now).filter(publication__lte=notify_until)
        return next_publications

    def handle(self, *args, **options):
        next_publications = self.next_publications()
        pending_emails = Mail.objects.all().filter(answered=False)
        subscribers = [
            sub.address for sub in DailyNotificationSubscriber.objects.all()]

        all_issues = Issue.objects.all()
        new_issues = []
        for issue in all_issues:
            if len(issue.historyelement_set.all()) is 1:
                new_issues.append(issue)

        fromaddr = settings.EMAIL_USERNAME

        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['Subject'] = "PrivacyScore: Daily Notification"

        body = """Hello Operator,

here is your daily privacyscore notification."""

        if len(pending_emails) > 0:
            body += """\n\nCurrently we have """ + \
                str(len(pending_emails)) + \
                """ e-mails waiting for an answer:\n"""
            for pemail in pending_emails:
                body += "\t" + pemail.title + "\n"
                if pemail.url != "":
                    body += "\t\turl=" + pemail.url + "\n"
                else:
                    body+= "\t\tnot linked to any url or issue\n"
            body += "\n\n"
        if len(next_publications) > 0:
            body += str(len(next_publications)) + \
                " vulnerable result(s) will be published in the next 7 days:\n"
            for issue in next_publications:
                body += "\t" + issue.problem_class.title + " on " + issue.url + "\n"
            body += "\n\n"
        if len(new_issues) > 0:
            body += str(len(new_issues)) + \
                " issues have been created and are ready for a notification."
            body += "\n\n"

        if len(pending_emails) == 0 and len(next_publications) == 0 and len(new_issues) == 0:
            print("DailyMail not required (nothing to do)")
        else:
            body += "\nSo long and thanks for all the fish,\n\nDaily Notification Cronjob"
            msg.attach(MIMEText(body, 'plain'))

            s = smtplib.SMTP_SSL(
                host=settings.EMAIL_SMTP_SERVER, port=settings.EMAIL_SMTP_PORT)
            s.login(fromaddr, settings.EMAIL_PASSWORD)

            for r in subscribers:
                toaddr = r
                msg['To'] = toaddr
                s.sendmail(fromaddr, toaddr, msg.as_string())
            s.quit()
            print("Mail send!")
