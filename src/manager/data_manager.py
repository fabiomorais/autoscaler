import threading as t
import time

from metric_util import get_monitoring_interval
from database_helper import create_or_update_metric_average_view_by_server
from database_helper import create_or_update_metric_view
from database_helper import create_or_update_uptime_vm_view

class Manager(t.Thread):

	def __init__(self, env, delay, iterations, server_id):
		t.Thread.__init__(self)
		self.environment	= env
		self.delay 		= delay
		self.iterations 	= iterations
		self.server_id		= server_id

	def run(self):

		ct = 0
		while ct < self.iterations:
			
			time.sleep(self.delay)

			ct += 1
			print 'Manager: {0}'.format(ct)

			metric_list		= self.environment.metric_list

			for x in range(0, len(metric_list)):

				metric_type			= metric_list[x]
				current_time 		= time.time()
				monitoring_interval	= get_monitoring_interval(current_time, self.environment.monitoring_period)

				create_or_update_metric_average_view_by_server(self.environment, metric_type, monitoring_interval, self.server_id)
				#create_or_update_metric_view(self.environment, metric_type, monitoring_interval)
				#create_or_update_uptime_vm_view(self.environment, monitoring_interval)

