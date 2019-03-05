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
            if "final_url" in result:
                url = result["final_url"]
            else:
                url = ""
            if "leaks" in result:
                leaks = result["leaks"]
            else:
                leaks = []
            if "support_mails" in result:
                mails = result["support_mails"]
            else:
                mails = []
            if len(leaks) > 0 and url != "":
                for leak in leaks:
                    issue = Issue(url=url, problem=leak, scan_result=scan)
                    issue.save()
                    # set state
                    state = State.objects.get(id=1)
                    history = HistoryElement(operator="PrivacyScore Scanner",  state=state, issue=issue)
                    history.save()
                    # create email addresses
                    for email in mails:
                        e = Address(address=email, issue=issue)
                        e.save()
                print(pk, leaks, mails)
