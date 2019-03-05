from django.core.management.base import BaseCommand, CommandError
from ticketsystem.models import HistoryElement
from ticketsystem.models import State

class Command(BaseCommand):
    help = 'Rescans unfixed issues'

    def handle(self, *args, **options):
        rescan_urls = {}

        issues = Issue.objects.all()
        for issue in issues:
            if issue.historyelement_set.all().last().title != "Fixed":
                rescan_urls.add(issue.url)

        for url in rescan_urls:
            site = Sites.objects().all().filter(url=url).latest('pk')
            site.scan()
