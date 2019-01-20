from django.shortcuts import render
from django.http import HttpResponse
from ticketsystem.models import Issue
from ticketsystem.models import State
from ticketsystem.models import Mail
from ticketsystem.models import ProblemClass
from ticketsystem.models import Address
from ticketsystem.models import Attachment
from ticketsystem.models import HistoryElement
import smtplib
from ticketsystem.models import DailyNotificationSubscriber
from django.conf import settings

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils as email_lib
# Create your views here.


def dashboard(request):
    all_issues = Issue.objects.all()
    pending_emails = Mail.objects.all().filter(answered=False)
    unsorted = len(Mail.objects.all().filter(url=""))
    new_issues = []
    for issue in all_issues:
        if len(issue.historyelement_set.all()) is 1:
            new_issues.append(issue)


    subscribe = request.POST.get('subscription', "")
    sub_mail = request.POST.get('email', "")

    if subscribe is not "" and sub_mail is not "":
        if subscribe == "Subscribe":
            sub = DailyNotificationSubscriber(address=sub_mail)
            sub.save()
        if subscribe == "Unsubscribe":
            subs = DailyNotificationSubscriber.objects.all().filter(address=sub_mail)
            for sub in subs:
                sub.delete()

    context = {
        'subsection': "Dashboard",
        'emails': pending_emails,
        'unsorted': unsorted,
        'notifications': [
            {'id': issue.id,
            'url': issue.url,
            'problemclass': issue.problem_class,
            'date': issue.historyelement_set.all().first().date} for issue in new_issues
            ]
    }
    return render(request, 'ticketsystem/dashboard.html', context)


def inject_testdata_view(request):
    problemclasses = ProblemClass.objects.all()

    got_request = False
    if request.method == 'POST':
        url = request.POST.get('url', "")
        emails = request.POST.get('emails', "")
        problemclass = request.POST.get('problemclass', "")

        if url is not "" and emails is not "" and problemclass is not "":
            got_request = True
            # create issue
            pclass = ProblemClass.objects.get(id=problemclass)
            issue = Issue(url=url, problem_class=pclass)
            issue.save()
            # set state
            state = State.objects.get(id=1)
            history = HistoryElement(state=state, issue=issue)
            history.save()
            # create email addresses
            for email in emails.split("; "):
                e = Address(address=email, issue=issue)
                e.save()

    context = {
        'subsection': "Create Issue",
        'got_request': got_request,
        'classes': [
            {'id': clazz.id, 'title': clazz.title} for clazz in problemclasses
            ]
    }
    return render(request, 'ticketsystem/inject_issue.html', context)


def open_issue_list_view(request):
    search = request.GET.get('search', "")
    issues = Issue.objects.all()

    search_results = []
    for issue in issues:
        state = issue.historyelement_set.all().order_by('-date').first().state.title
        if search in issue.url or search in issue.problem_class.title or search in state:
            search_results.append(issue)

    context = {
        'subsection': "Open Issues",
        'issues': [
            {'id': issue.id,
            'url': issue.url,
            'status': issue.historyelement_set.all().order_by('-date').first().state.title,
            'problem': issue.problem_class.title,
            'creation': issue.historyelement_set.all().order_by('-date').last().date,
            'publication': issue.publication,
            } for issue in search_results
            ],
        }
    return render(request, 'ticketsystem/issue_list_view.html', context)


def issue_view(request):
    id = request.GET['id']
    issue = Issue.objects.get(id=id)
    emails = Mail.objects.filter(url=issue.url).order_by("id")
    history_elements = issue.historyelement_set.all().order_by('date')
    more_issues_for_url = Issue.objects.filter(url=issue.url).exclude(id=id)
    # ToDo: error handling in case no id given
    context = {
        'subsection': issue.problem_class.title + " on " + issue.url,
        'id': id,
        'url': issue.url,
        'publication_date': issue.publication,
        'status': history_elements.last().state.title,
        'description': issue.problem_class.description,
        'emails': emails,
        'history': [
            {'date': element.date, 'description': element.state.title, 'comment': element.comment} for element in history_elements
            ],
        'more_issues_for_url': [
            {'id': next_issue.id, 'problem_class': next_issue.problem_class.title} for next_issue in more_issues_for_url
            ]
        }
    return render(request, 'ticketsystem/issue_detail_view.html', context)


def url_view(request):
    url = request.GET.get('url', "")
    issues = Issue.objects.all().filter(url=url)

    context = {
        'subsection': "Issues for url " + url,
        'issues': [
            {
            'id': issue.id,
            'url': issue.url,
            'status': issue.historyelement_set.all().order_by('-date').first().state.title,
            'problem': issue.problem_class.title,
            'creation': issue.historyelement_set.all().order_by('-date').last().date
            } for issue in issues
            ],
        }

    return render(request, 'ticketsystem/url_view.html', context)


def email_view(request):
    id = request.GET.get('id', 0)
    answered = request.GET.get('answered', "")
    link_to = request.GET.get('link_to', "")

    if link_to != "":
        emails = Mail.objects.all().filter(id=id)
        emails.update(url=link_to)

    set_answered = answered is not ""
    email = Mail.objects.get(id=id)
    issues_for_url = []
    if email.url != "":
        issues_for_url = Issue.objects.filter(url=email.url)
    print(issues_for_url)

    attachments = [att.filename for att in Attachment.objects.all().filter(mail=email)]
    urls = {issue.url for issue in Issue.objects.all()}

    if set_answered:
        issues = Issue.objects.filter(url=email.url)
        emails = Mail.objects.all().filter(id=id)
        emails.update(answered=True)
        for issue in issues:
            state = State.objects.get(id=3)
            history = HistoryElement(state=state, issue=issue)
            history.save()

    context = {
        'subsection': "E-Mail",
        'id': email.id,
        'url': email.url,
        'sender': email.sender,
        'receiver': email.receiver,
        'subject': email.title,
        'content': email.body,
        'message_id': email.message_id,
        'references': email.references,
        'attachments': attachments,
        'issues_for_url': issues_for_url,
        'urls': urls,
        }
    return render(request, 'ticketsystem/email_detail_view.html', context)


def closed_issue_list_view(request):
    context = {'subsection': "Closed Issues"}
    return render(request, 'ticketsystem/issue_list_view.html', context)


def statistics_view(request):
    context = {'subsection': "Statistics"}
    return render(request, 'ticketsystem/statistics.html', context)


def unsorted_emails_view(request):
    emails = Mail.objects.all().filter(url="")

    context = {
        'subsection': "Unsorted E-Mails",
        'emails': emails
        }
    return render(request, 'ticketsystem/unsorted_emails.html', context)

def notification_send_view(request):
    receiver = request.POST.getlist('receiver')
    emails = [email for email in receiver if email is not ""]
    title = request.POST.get('title')
    body = request.POST.get('content')
    url = request.POST.get('url', "")
    answer_to = request.POST.get('answer_to', 0)
    message_id = request.POST.get("message_id", "")
    references = request.POST.get("references", "")

    # update state
    if url is not "":
        issues = Issue.objects.filter(url=url)
        if answer_to is 0:
            state = State.objects.get(id=2)
            import pytz
            from datetime import datetime, timedelta
            u = datetime.now(pytz.utc)  # now
            d = timedelta(days=settings.DAYS_TILL_AUTO_DISCLOSURE)  # disclosure in 14 days
            t = u + d                   # t is the sum of now + 14 days
            none_issues = issues.filter(publication=None)
            none_issues.update(publication=t)
            pub_state = State.objects.get(id=5)
            for issue in issues:
                history = HistoryElement(comment="Set to " + str(t), state=pub_state, issue=issue)
                history.save()
        else:
            state = State.objects.get(id=3)
            email = Mail.objects.all().filter(id=answer_to)
            email.update(answered=True)
        for issue in issues:
            history = HistoryElement(state=state, issue=issue)
            history.save()

    # ToDo: send email
    fromaddr = settings.EMAIL_USERNAME

    # create mail objects for issue / url
    for toaddr in emails:
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['Subject'] = title

        if message_id != "":
            msg.add_header('In-Reply-To', message_id)
            msg.add_header('References', references + " " + message_id)

        msg.attach(MIMEText(body, 'plain'))

        s = smtplib.SMTP_SSL(host=settings.EMAIL_SMTP_SERVER, port=settings.EMAIL_SMTP_PORT)
        s.login(fromaddr, settings.EMAIL_PASSWORD)
        msg["Message-ID"] = email_lib.make_msgid()



        mail = Mail(title=title, message_id=msg["Message-ID"], answered=True, direction=True, sender="PrivacyScore", receiver=toaddr, body=body, url = url)
        mail.save()

        msg['To'] = toaddr
        s.sendmail(fromaddr, toaddr, msg.as_string())
        s.quit()

    context = {
        'subsection': "Notification send",
        'emails': emails,
        'title': title,
        'body': body,
        }
    return render(request, 'ticketsystem/mail_send.html', context)

def notification_view(request):
    id = request.GET.get('id', 0)
    if id is 0:
        pass
        # todo: send to error page

    issue = Issue.objects.get(id=id)
    text = issue.problem_class.email_body
    addresses = Address.objects.filter(issue=issue)

    context = {
        'subsection': "Notification",
        'issue': {
            'id': issue.id,
            'url': issue.url,
            'problemclass': issue.problem_class,
            'title': "Schwachstellen auf Ihrer Webseite ( " + issue.url + " )",
            'possible_addresses': [a.address for a in addresses],
            'description': text,
            }
        }
    return render(request, 'ticketsystem/issue_notification_form.html', context)
