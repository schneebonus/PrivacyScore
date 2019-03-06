from django.core.management.base import BaseCommand, CommandError
from ticketsystem.models import HistoryElement
from ticketsystem.models import State
from ticketsystem.models import Issue
from privacyscore.backend.models import Site
import re

class Command(BaseCommand):
    help = 'Rescans unfixed issues'

    def handle(self, *args, **options):
        rescan_urls = set()

        issues = Issue.objects.all()
        for issue in issues:
            if issue.historyelement_set.all().last().state.title != "Fixed":
                rescan_urls.add(issue.url)

        for url in rescan_urls:
            print("rescan of " + url)

            cleaned_url = self.clean_url(url)
            print(cleaned_url)

            sites_http = Site.objects.filter(url="http://" + cleaned_url + "/")
            sites_https = Site.objects.filter(url="https://" + cleaned_url + "/")
            if len(sites_http) is not 0:
                sites_http[0].scan()
            elif len(sites_https) is not 0:
                sites_https[0].scan()
            elif cleaned_url.startswith("www."):
                without_www = cleaned_url.replace("www.", "")
                sites_http_no_www = Site.objects.filter(url="http://" + without_www + "/")
                sites_https_no_www = Site.objects.filter(url="https://" + without_www + "/")
                if len(sites_http_no_www) is not 0:
                    sites_http_no_www[0].scan()
                elif len(sites_https_no_www) is not 0:
                    sites_https_no_www[0].scan()
            else:
                print("Error: Could not find site for URL!")

    def clean_url(self, url):
        regex = "^https?:\/\/(.*)(\/.*)$"
        searchObj = re.search( regex, url)
        return searchObj.group(1)
