from django.db import models
from django import forms
from datetime import datetime
from enum import Enum
from django.utils.timezone import now
from privacyscore.backend.models import ScanResult
import pytz
# from datetime import datetime, timedelta

class State(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.title

class DailyNotificationSubscriber(models.Model):
    address = models.CharField(max_length=100)
    def __str__(self):
        return self.address

class ProblemClass(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    email_body = models.TextField()
    def __str__(self):
        return self.title

class Issue(models.Model):
    url = models.CharField(max_length=100)
    problem = models.CharField(max_length=100, default="unknown")
    scan_result = models.ForeignKey(ScanResult, on_delete=models.CASCADE, default=0)
    # problem_class = models.ForeignKey(ProblemClass, on_delete=models.CASCADE)
    publication = models.DateTimeField(blank=True, null=True)
    prevent_publication = models.BooleanField(default=False)
    def __str__(self):
        return self.url + ":"+self.problem

class Address(models.Model):
    address = models.CharField(max_length=100)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    def __str__(self):
        return self.address

class HistoryElement(models.Model):
    date = models.DateTimeField(
        default=datetime.now, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    comment = models.CharField(max_length=100, default="", blank=True)
    operator = models.CharField(max_length=100)
    def __str__(self):
        return str(self.state) + " for " + str(self.issue)

class Mail(models.Model):
    title = models.CharField(max_length=200)
    direction = models.BooleanField(default=False) # outgoing is True, incoming is False
    sequence = models.IntegerField(default=0)
    sender = models.CharField(max_length=200)
    receiver = models.CharField(max_length=200)
    body = models.TextField()
    message_id = models.CharField(max_length=200)
    references = models.CharField(max_length=400, blank=True)
    answered = models.BooleanField(default=False)
    received_at = models.DateTimeField(default=now, blank=True)
    url = models.CharField(max_length=200)

    def __str__(self):
        return "%s -> %s -> %s" % (self.sender, self.title, self.receiver)

class Attachment(models.Model):
    filename = models.CharField(max_length=200)
    mail = models.ForeignKey(Mail, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.filename)
