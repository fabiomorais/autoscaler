import threading as t
import time

from database_helper import insert_metric_usage
from database_helper import insert_or_update_flavors
from database_helper import insert_or_update_servers
from database_util import get_database_timestamp_format
from nova_util import get_server_list_json
from nova_util import get_flavor_list_json
from metric_util import get_monitoring_interval
from ceilometer_util import get_metric_data
from server_util import get_server_id

class Monitor(t.Thread):
    
    def __init__(self, env, delay, iterations, monitor_event, controller_event):

        t.Thread.__init__(self)
        self.delay              = delay
        self.iterations         = iterations
        self.environment        = env
        self.monitor_event      = monitor_event
        self.controller_event   = controller_event
        self.delay_correction   = 0
    
    def run(self):

        servers    = get_server_list_json(self.environment)
        flavors = get_flavor_list_json(self.environment)
    
        insert_or_update_flavors(self.environment, flavors)
        insert_or_update_servers(self.environment, servers)

        metric_type   = self.environment.metric_type
        
        ct = 0
        while ct < self.iterations:

            time.sleep(self.delay - self.delay_correction)
            
            print 'Monitor delay:', self.delay_correction
            
            if not self.controller_event == None:
                self.controller_event.wait()
                self.controller_event.clear()
            
            if (not self.monitor_event == None) and (self.monitor_event.is_set()):
                self.monitor_event.clear()

            start_time = time.time()
                
            ct += 1
            print 'Monitor: {0}'.format(ct)

            servers = get_server_list_json(self.environment)
            flavors = get_flavor_list_json(self.environment)
    
            insert_or_update_flavors(self.environment, flavors)
            insert_or_update_servers(self.environment, servers)
    
            for x in range(0, len(servers['servers'])):    
                
                server_id           = get_server_id(servers, x)
                current_time        = time.time()
                monitoring_interval = get_monitoring_interval(current_time, self.environment.monitoring_period)
                
                metric_data         = get_metric_data(self.environment, metric_type, server_id, monitoring_interval)
                
                for z in range(0, len(metric_data)):
    
                    tmp_metric_util     = metric_data[z]['counter_volume']
                    tmp_timestamp       = metric_data[z]['timestamp']
                    
                    #print tmp_timestamp
                    
                    timestamp           = get_database_timestamp_format(tmp_timestamp, '%Y-%m-%dT%H:%M:%S')

                    insert_metric_usage(self.environment, metric_type, server_id, self.environment.project_id, timestamp, tmp_metric_util)
    
            if not self.monitor_event == None:
                self.monitor_event.set()
            
            #if(ct < 1):
    
            #    self.manager.start()
    
            self.delay_correction   = time.time() - start_time

