from django.core.management.base import BaseCommand, CommandError
from ticketsystem.models import HistoryElement
from ticketsystem.models import State
from ticketsystem.models import Issue
from ticketsystem.models import Address
import json
from privacyscore.backend.models import Scan
from privacyscore.backend.models import ScanResult

class Command(BaseCommand):
    help = 'Creates new issues from recent scan results'

    def handle(self, *args, **options):
        all_scan_results = ScanResult.objects.all() # .filter(issue_checked=False)

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
            # create new leaks (if not known already)
            if len(leaks) > 0 and url != "":
                for leak in leaks:
                    already_known = False
                    previous_issues = Issue.objects.all().filter(url=url).filter(problem=leak)
                    for issue in previous_issues:
                        state = issue.historyelement_set.all().order_by('-date').first().state.title
                        if state != "Fixed":
                            already_known = True
                    if already_known is False:
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
            #scan.issue_checked = True
            #scan.save()
            # close fixed issues (if no longer found)
            issues = Issue.objects.all().filter(url=url)
            for issue in issues:
                problem = issue.problem
                if problem not in leaks:
                    # could not find the problem
                    # seems to be fixed and the issue can get state=closed / fixed
                    state = State.objects.get(title="Fixed")
                    history = HistoryElement(operator="PrivacyScore Scanner",  state=state, issue=issue)
                    history.save()
