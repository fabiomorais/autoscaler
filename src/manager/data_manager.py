import threading as t
import time

from metric_util import get_monitoring_interval
from database_helper import create_or_update_metric_average_by_project
from database_helper import create_or_update_metric_by_project
from database_helper import create_or_update_uptime_vm_view

class Manager(t.Thread):

	def __init__(self, env, delay, iterations, manager_event, monitor_event):
		t.Thread.__init__(self)
		self.environment		= env
		self.delay 				= delay
		self.iterations 		= iterations
		self.manager_event 		= manager_event
		self.monitor_event		= monitor_event
		self.delay_correction	= 0
		
	def run(self):

		metric_type		= self.environment.metric_type
		
		ct = 0
		while ct < self.iterations:
			
			time.sleep(self.delay - self.delay_correction)

			print 'Manager delay:', self.delay_correction

			if not self.monitor_event == None:
				self.monitor_event.wait()
				self.monitor_event.clear()
			
			if (not self.manager_event == None) and (self.manager_event.is_set()):
				self.manager_event.clear()
			
			start_time = time.time()

			ct += 1
			print 'Manager: {0}'.format(ct)

			current_time 		= time.time()
			
			monitoring_interval	= get_monitoring_interval(current_time, self.environment.monitoring_period)
			
			create_or_update_metric_average_by_project(self.environment, metric_type, monitoring_interval)
			create_or_update_metric_by_project(self.environment, metric_type)
			create_or_update_uptime_vm_view(self.environment, monitoring_interval)

			if not self.manager_event == None:
				self.manager_event.set()
				
			self.delay_correction   = time.time() - start_time