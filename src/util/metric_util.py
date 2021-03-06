import time

def get_monitoring_interval(current_time, period):
	
	limit_monitoring_date 	= current_time - float(period)
	return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(current_time)), time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(limit_monitoring_date))

def get_meter_mean(meter_data):

	meter_util	= []

	for x in range(0, len(meter_data)):
		meter_util.append(meter_data[x]['counter_volume'])

	mean_meter_util	= "NULL"

	if(len(meter_util) > 0):
		return sum(meter_util) / float(len(meter_util))

	return mean_meter_util

