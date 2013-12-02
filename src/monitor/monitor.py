import threading as t
import time

from database_helper import insert_metric_usage
from database_helper import insert_or_update_flavors
from database_helper import insert_or_update_servers
from database_helper import insert_project
from database_util import get_database_timestamp_format
from nova_util import get_server_list_json
from nova_util import get_flavor_list_json
from metric_util import get_monitoring_interval
from ceilometer_util import get_metric_data
from server_util import get_server_id

class Monitor(t.Thread):
    
    def __init__(self, env, delay, iterations=1):

        t.Thread.__init__(self)
        self.delay          = delay
        self.iterations     = iterations
        self.environment    = env
    
    def run(self):

        servers    = get_server_list_json(self.environment)
        flavors = get_flavor_list_json(self.environment)
    
        insert_project(self.environment, self.environment.project_id, self.environment.project_name)
        insert_or_update_flavors(self.environment, flavors)
        insert_or_update_servers(self.environment, servers)

        ct = 0
        while ct < self.iterations:

            time.sleep(self.delay)
            
            ct += 1
            print 'Monitor: {0}'.format(ct)

            servers    = get_server_list_json(self.environment)
            flavors = get_flavor_list_json(self.environment)
    
            insert_or_update_flavors(self.environment, flavors)
            insert_or_update_servers(self.environment, servers)
    
            for x in range(0, len(servers['servers'])):    
                
                server_id           = get_server_id(servers, x)
                current_time         = time.time()
                monitoring_interval = get_monitoring_interval(current_time, self.environment.monitoring_period)
                metric_list          = self.environment.metric_list

                for y in range(0, len(metric_list)):

                    metric_type    = metric_list[y]
                    metric_data    = get_metric_data(self.environment, metric_type, server_id, monitoring_interval)
                    
                    for z in range(0, len(metric_data)):
    
                        tmp_metric_util     = metric_data[z]['counter_volume']
                        tmp_timestamp    = metric_data[z]['timestamp']
    
                        timestamp     = get_database_timestamp_format(tmp_timestamp, '%Y-%m-%dT%H:%M:%S')
    
                        insert_metric_usage(self.environment, metric_type, server_id, self.environment.project_id, timestamp, tmp_metric_util)
    
            #if(ct < 1):
    
            #    self.manager.start()
    

