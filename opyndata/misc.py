from datetime import datetime
from datetime import timedelta

def datenum_to_datetime(datenum):
    dt = datetime.fromordinal(int(datenum)) + timedelta(days=datenum%1) - timedelta(days = 366)
    return dt