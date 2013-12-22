import threading as t
import time

from metric_util import get_monitoring_interval
from database_helper import create_or_update_metric_average_by_project
from database_helper import create_or_update_metric_by_project
from database_helper import create_or_update_uptime_vm_view

class Manager(t.Thread):

	def __init__(self, env, delay, iterations):
		t.Thread.__init__(self)
		self.environment	= env
		self.delay 		= delay
		self.iterations 	= iterations

	def run(self):

		metric_type		= self.environment.metric_type
		
		ct = 0
		while ct < self.iterations:
			
			time.sleep(self.delay)

			ct += 1
			print 'Manager: {0}'.format(ct)

			current_time 		= time.time()
			monitoring_interval	= get_monitoring_interval(current_time, self.environment.monitoring_period)

			create_or_update_metric_average_by_project(self.environment, metric_type, monitoring_interval)
			create_or_update_metric_by_project(self.environment, metric_type)
			create_or_update_uptime_vm_view(self.environment, monitoring_interval)
