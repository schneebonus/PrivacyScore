from django.core.management.base import BaseCommand, CommandError
from ticketsystem.models import HistoryElement
from ticketsystem.models import State
import json
from privacyscore.backend.models import Scan
from privacyscore.backend.models import ScanResult

class Command(BaseCommand):
    help = 'Creates new issues from recent scan results'

    def handle(self, *args, **options):
        all_scan_results = ScanResult.objects.all()

        for scan in all_scan_results:
            pk = scan.pk
            result = scan.result
            if "leaks" in result:
                leaks = result["leaks"]
            else:
                leaks = []
            if "support_mails" in result:
                mails = result["support_mails"]
            else:
                mails = []
            print(pk, leaks, mails)
