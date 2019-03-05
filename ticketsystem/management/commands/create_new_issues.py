from django.core.management.base import BaseCommand, CommandError
from ticketsystem.models import HistoryElement
from ticketsystem.models import State
from privacyscore.backend.models import Scan
from privacyscore.backend.models import ScanResult

class Command(BaseCommand):
    help = 'Creates new issues from recent scan results'

    def handle(self, *args, **options):
        all_scan_results = ScanResult.objects.all()

        print(all_scan_results)
