from datetime import datetime

from dateutil.parser import parse


def parse_date(value):
    if isinstance(value, str):
        return parse(value).date()
    elif isinstance(value, datetime):
        return value.date()
    return value
