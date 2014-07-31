import time

from datetime import datetime

def get_database_timestamp_format(timestamp, pattern):
	
	timestamp_date	= datetime.strptime(timestamp, pattern)

	timestamp_epoch = time.mktime(timestamp_date.timetuple())

	return datetime.fromtimestamp(timestamp_epoch).strftime('%Y-%m-%d %H:%M:%S')
