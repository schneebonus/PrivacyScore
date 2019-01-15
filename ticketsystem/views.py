from django.shortcuts import render
from django.http import HttpResponse
from ticketsystem.models import Issue
from ticketsystem.models import State
from ticketsystem.models import Mail
from ticketsystem.models import ProblemClass
from ticketsystem.models import Address
from ticketsystem.models import HistoryElement
# Create your views here.


def dashboard(request):
    all_issues = Issue.objects.all()

    new_issues = []
    for issue in all_issues:
        if len(issue.historyelement_set.all()) is 1:
            new_issues.append(issue)

    context = {
        'subsection': "Dashboard",
        'emails': [

        ],
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
            {'id' : clazz.id, 'title': clazz.title} for clazz in problemclasses
            ]
    }
    return render(request, 'ticketsystem/inject_issue.html', context)

def open_issue_list_view(request):
    issues = Issue.objects.all()
    context = {
        'subsection': "Open Issues",
        'issues': [
            {'id': issue.id, 'url': issue.url, 'status': '?', 'email': '?', 'creation': '?'} for issue in issues
            ],
        }
    return render(request, 'ticketsystem/issue_list_view.html', context)

def issue_view(request):
    id = request.GET['id']
    issue = Issue.objects.get(id=id)
    emails = Mail.objects.filter(url=issue.url)
    history_elements = issue.historyelement_set.all().order_by('-date')
    more_issues_for_url = Issue.objects.filter(url=issue.url).exclude(id=id)
    # ToDo: error handling in case no id given
    context = {
        'subsection': issue.problem_class.title + " on " + issue.url,
        'id': id,
        'url': issue.url,
        'publication_date': '?',
        'status': history_elements.first().state.title,
        'description': issue.problem_class.description + " ToDo: add individual details",
        'emails': [
            {'id': email.id, 'subject': email.title, 'representation': str(email)} for email in emails
            ],
        'history': [
            {'date': element.date, 'description': element.state.title} for element in history_elements
            ],
        'more_issues_for_url': [
            {'id': next_issue.id, 'problem_class': next_issue.problem_class.title} for next_issue in more_issues_for_url
            ]
        }
    return render(request, 'ticketsystem/issue_detail_view.html', context)

def email_view(request):
    context = {
        'subsection': "E-Mail",
        'id': "1",
        'sender': "mitarbeiter1@suunto.com",
        'receiver': "notify@privacyscore.org",
        'subject': "Re: Schwachstellen auf Ihrer Webseite (url: "+ url +")",
        'content': "Hallo,\nkönnen sie bitte weitere Informationen liefern?\n\nVielen Dank,\nMitarbeiter1",
        }
    return render(request, 'ticketsystem/email_detail_view.html', context)

def closed_issue_list_view(request):
    context = {'subsection': "Closed Issues"}
    return render(request, 'ticketsystem/issue_list_view.html', context)

def statistics_view(request):
    context = {'subsection': "Statistics"}
    return render(request, 'ticketsystem/statistics.html', context)

def notification_send_view(request):
    receiver = request.POST.getlist('receiver')
    title = request.POST.get('title')
    body = request.POST.get('content')
    id = request.POST.get('id')

    # update state
    print(id)
    issue = Issue.objects.get(id=id)
    state = State.objects.get(id=2)
    history = HistoryElement(state=state, issue=issue)
    history.save()

    # create mail objects for issue / url
    for r in emails:
        mail = Mail(title=title, sender="PrivacyScore", receiver=r, body=body, url = issue.url)
        mail.save()

    # ToDo: send email

    emails = [email for email in receiver if email is not ""]
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

    text ="""Sehr geehrte Damen und Herren,

ToDo: echte Texte aus Django Model.

Mit freundlichen Grüßen,
Das PrivacyScore Team
"""

    issue = Issue.objects.get(id=id)
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