
import json
import crawler.smailcrawler as crawler
from typing import Dict, Union

from urllib.parse import urlparse


test_name = 'mailcrawler'
test_dependencies = []


def test_site(url: str, previous_results: dict, **options) -> Dict[str, Dict[str, Union[str, bytes]]]:
    # Calls the E-Mail Crawler and returns a list of emails
    result = {}

    print("Mail Crawler for " + url)

    # mails = crawler.scan(url)
    mails = ["a@b.de"]

    result['mailcrawler'] = {
        'mime_type': 'application/json',
        'data': json.dumps(mails).encode(),
    }

    return result


def process_test_data(raw_data: list, previous_results: dict, **options) -> Dict[str, Dict[str, object]]:
    result = {"mailcrawler_finished": True}

    if raw_data['mailcrawler']['data'] == b'':
        result['has_mails'] = False
        return result
    else:
        potential_support_mails = json.loads(raw_data['mailcrawler']['data'].decode())
        result['has_mails'] = True
        result['support_mails'] = potential_support_mails

    return result
