

from ...config import date_format

def checkNone(value, format): return format(value) if value is not None else None
def checkNoneDate(value): return value.strftime(format=date_format) if value is not None else None

