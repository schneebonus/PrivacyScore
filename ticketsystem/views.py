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
import pytz
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.utils as email_lib
from django.contrib.auth.decorators import login_required
from ticketsystem.utils import utils
import imaplib
from django.shortcuts import redirect
# Create your views here.

@login_required
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
            'problemclass': issue.problem,
            'date': issue.historyelement_set.all().first().date} for issue in new_issues
            ]
    }
    return render(request, 'ticketsystem/dashboard.html', context)

@login_required
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
            history = HistoryElement(operator="PrivacyScore Scanner",  state=state, issue=issue)
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

@login_required
def open_issue_list_view(request):
    search = request.GET.get('search', "")
    issues = Issue.objects.all()

    search_results = []
    for issue in issues:
        state = issue.historyelement_set.all().order_by('-date').first().state.title
        if (search in issue.url or search in issue.problem or search in state) and state != "Fixed":
            search_results.append(issue)

    context = {
        'subsection': "Open Issues",
        'issues': [
            {'id': issue.id,
            'url': issue.url,
            'status': issue.historyelement_set.all().order_by('-date').first().state.title,
            'problem': issue.problem,
            'creation': issue.historyelement_set.all().order_by('-date').last().date,
            'publication': issue.publication,
            } for issue in search_results
            ],
        }
    return render(request, 'ticketsystem/issue_list_view.html', context)

@login_required
def issue_view(request):
    id = request.GET['id']
    action = request.GET.get('action', "")

    issue = Issue.objects.get(id=id)

    if action == "prevent":
        Issue.objects.all().filter(id=id).update(prevent_publication=True)
        pub_state = State.objects.get(id=6)
        history = HistoryElement(operator=request.user.username, comment="Prevented! No publication allowed!", state=pub_state, issue=issue)
        history.save()
    elif action == "restart":
        Issue.objects.all().filter(id=id).update(prevent_publication=False)
        pub_state = State.objects.get(id=5)
        history = HistoryElement(operator=request.user.username, comment="Allowed!", state=pub_state, issue=issue)
        history.save()
        # calculate new publication date
        u = datetime.now(pytz.utc)  # now
        d = timedelta(days=settings.DAYS_TILL_AUTO_DISCLOSURE)  # disclosure in 14 days
        t = u + d                   # t is the sum of now + 14 days
        Issue.objects.all().filter(id=id).update(publication=t)
        pub_state = State.objects.get(id=5)
        history = HistoryElement(operator=request.user.username, comment="Set to " + str(t), state=pub_state, issue=issue)
        history.save()
    elif action == "extend":
        new_publication = issue.publication + timedelta(days=14)
        Issue.objects.all().filter(id=id).update(publication=new_publication)
        pub_state = State.objects.get(id=5)
        history = HistoryElement(operator=request.user.username, comment="Set to " + str(new_publication), state=pub_state, issue=issue)
        history.save()

    emails = Mail.objects.filter(url=issue.url).order_by("id")
    history_elements = issue.historyelement_set.all().order_by('date')
    more_issues_for_url = Issue.objects.filter(url=issue.url).exclude(id=id)
    # ToDo: error handling in case no id given
    issue = Issue.objects.get(id=id)
    context = {
        'subsection': issue.problem + " on " + issue.url,
        'id': id,
        'url': issue.url,
        'publication_date': issue.publication,
        'prevent_publication': issue.prevent_publication,
        'status': history_elements.last().state.title,
        'description': issue.problem,
        'emails': emails,
        'history': [
            {'date': element.date, 'description': element.state.title, 'comment': element.comment, 'operator': element.operator} for element in history_elements
            ],
        'more_issues_for_url': [
            {'id': next_issue.id, 'problem_class': next_issue.problem} for next_issue in more_issues_for_url
            ]
        }
    return render(request, 'ticketsystem/issue_detail_view.html', context)

@login_required
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
            'problem': issue.problem,
            'creation': issue.historyelement_set.all().order_by('-date').last().date
            } for issue in issues
            ],
        }

    return render(request, 'ticketsystem/url_view.html', context)

@login_required
def email_view(request):
    id = request.GET.get('id', 0)
    answered = request.GET.get('answered', "")
    link_to = request.GET.get('link_to', "")

    if link_to != "":
        emails = Mail.objects.all().filter(id=id)
        emails.update(url=link_to)
        issues = Issue.objects.all().filter(url=link_to)
        for issue in issues:
            state = State.objects.get(id=4)
            history = HistoryElement(
                operator=request.user.username,state=state, issue=issue, comment="Linked e-mail to " + link_to + ".")
            history.save()

    set_answered = answered is not ""
    email = Mail.objects.get(id=id)
    issues_for_url = []
    if email.url != "":
        issues_for_url = Issue.objects.filter(url=email.url)

    attachments = [att.filename for att in Attachment.objects.all().filter(mail=email)]
    urls = {issue.url for issue in Issue.objects.all()}

    if set_answered:
        issues = Issue.objects.filter(url=email.url)
        emails = Mail.objects.all().filter(id=id)
        emails.update(answered=True)
        for issue in issues:
            state = State.objects.get(id=3)
            history = HistoryElement(operator=request.user.username, state=state, issue=issue)
            history.save()

    context = {
        'subsection': "E-Mail",
        'id': email.id,
        'url': email.url,
        'sender': email.sender,
        'answered': email.answered,
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

@login_required
def closed_issue_list_view(request):
    search = request.GET.get('search', "")

    issues = Issue.objects.all()

    search_results = []
    for issue in issues:
        state = issue.historyelement_set.all().order_by('-date').first().state.title
        if (search in issue.url or search in issue.problem or search in state) and state == "Fixed":
            search_results.append(issue)

    context = {
        'subsection': "Closed Issues",
        'issues': [
            {'id': issue.id,
            'url': issue.url,
            'status': issue.historyelement_set.all().order_by('-date').first().state.title,
            'problem': issue.problem,
            'creation': issue.historyelement_set.all().order_by('-date').last().date,
            'publication': issue.publication,
            } for issue in search_results
            ],
        }
    return render(request, 'ticketsystem/issue_list_view.html', context)

@login_required
def statistics_view(request):
    issues = Issue.objects.all()
    total_open_issues = 0
    total_closed_issues = 0
    issue_urls = set()
    for issue in issues:
        state = issue.historyelement_set.all().order_by('-date').first().state.title
        if state == "Fixed":
            total_closed_issues += 1
        else:
            total_open_issues += 1
        issue_urls.add(issue.url)
    total_issues = len(issues)
    total_urls = len(issue_urls)
    mails = Mail.objects.all()
    total_mails = len(mails)
    mails_outgoing = Mail.objects.all().filter(direction=True)
    total_mails_outgoing = len(mails_outgoing)
    mails_incoming = Mail.objects.all().filter(direction=False)
    total_mails_incoming = len(mails_incoming)

    context = {'subsection': "Statistics",
        'total_open_issues': total_open_issues,
        'total_closed_issues': total_closed_issues,
        'total_issues': total_issues,
        'total_urls': total_urls,
        'total_mails': total_mails,
        'total_mails_outgoing': total_mails_outgoing,
        'total_mails_incoming': total_mails_incoming,
        }
    return render(request, 'ticketsystem/statistics.html', context)

@login_required
def unsorted_emails_view(request):
    emails = Mail.objects.all().filter(url="")

    context = {
        'subsection': "Unsorted E-Mails",
        'emails': emails
        }
    return render(request, 'ticketsystem/unsorted_emails.html', context)


@login_required
def delete_email_view(request):
    email_id = request.POST.get('id', "0")
    email = Mail.objects.all().get(id=email_id)
    uid = email.sequence

    M = imaplib.IMAP4_SSL(settings.EMAIL_IMAP_SERVER, settings.EMAIL_IMAP_PORT)
    M.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
    print(M.list()[1])
    M.select("INBOX", False)

    typ, data = M.search(None, 'ALL')
    for num in data[0].split():
        tmp, uid_num = M.fetch(num, '(UID)')
        uid_num = utils.extract_uid(uid_num)
        print(type(uid_num), type(uid))
        if str(uid_num) == str(uid):
            M.store(num, '+FLAGS', '\\Deleted')
    M.expunge()

    M.close()
    M.logout()

    email.delete()
    return redirect('dashboard')

@login_required
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
    if url is not "" and len(emails) is not 0:
        issues = Issue.objects.filter(url=url)
        if answer_to is 0:
            state = State.objects.get(id=2)
            u = datetime.now(pytz.utc)  # now
            d = timedelta(days=settings.DAYS_TILL_AUTO_DISCLOSURE)  # disclosure in 14 days
            t = u + d                   # t is the sum of now + 14 days
            none_issues = issues.filter(publication=None)
            none_issues.update(publication=t)
            pub_state = State.objects.get(id=5)
            for issue in issues:
                history = HistoryElement(operator=request.user.username, comment="Set to " + str(t), state=pub_state, issue=issue)
                history.save()
        else:
            state = State.objects.get(id=3)
            email = Mail.objects.all().filter(id=answer_to)
            email.update(answered=True)
        for issue in issues:
            history = HistoryElement(operator=request.user.username, state=state, issue=issue)
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

@login_required
def notification_view(request):
    id = request.GET.get('id', 0)
    if id is 0:
        pass
        # todo: send to error page

    issue = Issue.objects.get(id=id)
    all_issues_for_url = Issue.objects.filter(url=issue.url)
    open_issues_for_url = set()
    for issue in all_issues_for_url:
        state = issue.historyelement_set.all().order_by('-date').first().state.title
        if state != "Fixed":
            open_issues_for_url.add(issue)

    addresses = set()
    for i in all_issues_for_url:
        addresses_of_issue = Address.objects.filter(issue=i)
        for a in addresses_of_issue:
            addresses.add(a)

    context = {
        'subsection': "Notification",
        'issue': {
            'id': issue.id,
            'url': issue.url,
            'possible_addresses': {a.address for a in addresses},
            'all_issues_for_url': open_issues_for_url,
            }
        }
    return render(request, 'ticketsystem/issue_notification_form.html', context)
