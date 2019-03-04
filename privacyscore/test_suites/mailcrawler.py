
import json
# import mail_crawler
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
    potential_support_mails = ["test@f5w.de"]
    # potential_support_mails = mail_crawler.scan(parsed_url)

    raw_requests["mailcrawler"] = {
        'mime_type': 'application/json',
        'data': json.dumps(potential_support_mails),
    }

    return raw_requests


def process_test_data(raw_data: list, previous_results: dict, **options) -> Dict[str, Dict[str, object]]:
    result = {"mailcrawler_finished": True}

    if raw_data['jsonresult']['data'] == b'':
        result['mx_has_ssl'] = False
        return result


    potential_support_mails = raw_data['potential_support_mails']

    return {
        'potential_support_mails': potential_support_mails,
    }
