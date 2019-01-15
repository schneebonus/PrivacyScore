from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.dashboard, name="dashboard"),
    url(r'^open$', views.open_issue_list_view, name="open_issues"),
    url(r'^closed$', views.closed_issue_list_view, name="closed_issues"),
    url(r'^statistics$', views.statistics_view, name="statistics"),
    url(r'^notify$', views.notification_view, name="notification"),
    url(r'^issue$', views.issue_view, name="issue"),
    url(r'^email$', views.email_view, name="email"),
    url(r'^inject$', views.inject_testdata_view, name="inject"),
    url(r'^notification_send$', views.notification_send_view, name="send"),
    url(r'^unsorted_emails$', views.unsorted_emails_view, name="unsorted_emails"),
]
