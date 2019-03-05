
import json
# import mail_crawler
from typing import Dict, Union

from urllib.parse import urlparse
from ticketsystem.models import Address

test_name = 'mailcrawler'
test_dependencies = []


def test_site(url: str, previous_results: dict, **options) -> Dict[str, Dict[str, Union[str, bytes]]]:
    # Calls the E-Mail Crawler and returns a list of emails
    result = {}
    parsed_url = urlparse(url)

    mails = ["test@f5w.de", "something@f5w.de"]
    # mails = mail_crawler.scan(parsed_url)

    result['mailcrawler'] = {
        'mime_type': 'application/json',
        'data': json.dumps(mails).encode(),
    }

    return result


def process_test_data(raw_data: list, previous_results: dict, **options) -> Dict[str, Dict[str, object]]:
    result = {"mailcrawler_finished": True}

    if raw_data['jsonresult']['data'] == b'':
        result['mx_has_ssl'] = False
        return result


    potential_support_mails = raw_data['potential_support_mails']

    return {
        'potential_support_mails': potential_support_mails,
    }
