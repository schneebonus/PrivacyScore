
import json
import mail_crawler
from typing import Dict, Union

from ticketsystem.models import Address

test_name = 'mailcrawler'
test_dependencies = []


def test_site(url: str, previous_results: dict, **options) -> Dict[str, Dict[str, Union[str, bytes]]]:
    # Calls the E-Mail Crawler and returns a list of emails
    raw_requests = {
        'url': {
            'mime_type': 'text/plain',
            'data': url.encode(),
        }
    }
    parsed_url = urlparse(url)

    # ToDo: call scanner here
    potential_support_mails = mail_crawler.scan(parsed_url)

    # Add results to raw_requests
    raw_requests['potential_support_mails'] = potential_support_mails

    return raw_requests


def process_test_data(raw_data: list, previous_results: dict, **options) -> Dict[str, Dict[str, object]]:
    potential_support_mails = json.loads(raw_data['potential_support_mails'].decode())

    for email in potential_support_mails:
        email = Address(address=email, url=url) # ToDo: emails should be linked to urls - not issues
        email.save()

    # An example for a return value of the process function.
    return {
        'potential_support_mails': potential_support_mails,
    }
