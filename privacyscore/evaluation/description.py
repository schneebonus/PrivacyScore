"""
This module defines textual representations/explanations for results of keys.
"""
from typing import Iterable, Tuple

from django.utils.translation import ugettext_lazy as _

from privacyscore.evaluation.result_groups import RESULT_GROUPS


def describe_locations(server_type: str, locations: list) -> str:
    """Describe a list of locations."""
    if not locations or locations == ['']:
        return _('The location of the %(server_type)s could not '
                 'be detected.') % {'server_type': server_type}
    if len(locations) == 1:
        return _('All %(server_type)s are located in %(country)s.') % {
            'server_type': server_type,
            'country': locations[0]
        }
    return _('The %(server_type)s are located in %(countries)s.') % {
        'server_type': server_type,
        'countries': ', '.join(locations[:-1]) + ' and {}'.format(locations[-1])
    }


# The mapping specifies a function for each key to create a description
# explaining the result to a user.
# TODO: multiple attributes should be describable together
# TODO: Cleaner solution? Inline lamdas are ugly and not flexible at all.
# TODO: Deterministic ordering. This defines the order of the descriptions which is not specified for a usual dict. Order could change on page reload!
MAPPING = {
    'general': {
        'third_parties_count': lambda v: _('The site does not use any third parties.') if v == 0 else _('The site is using %(count)d different third parties.') % {'count': v},
    },
    'privacy': {
        'a_locations': lambda v: describe_locations(_('web servers'), v),
        'mx_locations': lambda v: describe_locations(_('mail servers'), v),
    },
    'ssl': {
        'pfs': lambda v: _('The server is supporting perfect forward secrecy.') if v else _('The site is not supporting perfect forward secrecy.'),
    },
}


def describe_result(result: dict) -> Iterable[Tuple[str, Iterable[str]]]:
    """Describe each group of a result."""
    for group, group_name in RESULT_GROUPS.items():
        if group not in MAPPING or group not in result:
            continue
        yield group_name, describe_group(group, result[group])


def describe_group(group: str, results: dict) -> Iterable[str]:
    """Describe result of a single group."""
    for key, desc in MAPPING[group].items():
        if key not in results:
            continue
        yield desc(results[key])
