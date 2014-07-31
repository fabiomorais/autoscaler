import threading as t
import time

from predictor_helper import select_predictor
from predictor_helper import get_predictor_by_name
from capacity_planner import capacity_planning
from database_helper import get_last_metric_element_by_project
from nova_util import get_number_of_servers
from nova_util import get_number_of_cores_by_server
from actuator import Actuator

def there_is_violation(env, metric_type):
    
    element = get_last_metric_element_by_project(env, metric_type)
    
    if float(element[0][1]) >= float(env.violation_value * 100):
        return True
    return False

def is_selection_point(selection_time, selection_peiodicity):
    if ((int(selection_time) == int(selection_peiodicity)) or (int(selection_time) == 0)):
        return True
    return False

def run_predictions(env, predictors_list):
    
    events  = []
    
    for p in predictors_list:
        event       = t.Event()
        predictor   = get_predictor_by_name(env, p, event)
        predictor.start()
        
        events.append(event)
    
    return events
        
def wait_for_all_events(events):
    for e in events:
        e.wait()

class Controller(t.Thread):
            
    predictor_default  = None
    predictor          = None
    
    def __init__(self, env, delay, predictor_default, iterations, controller_event, manager_event):

        t.Thread.__init__(self)
        
        self.delay              = delay
        self.iterations         = iterations
        self.environment        = env
        self.predictor_default  = predictor_default
        self.events             = None
        self.controller_event   = controller_event
        self.manager_event      = manager_event
        self.delay_correction   = 0
    
    def run(self):

        if not (self.predictor_default == None):
            self.predictor  = get_predictor_by_name(self.environment, self.predictor_default, None)
            
        metric_type         = self.environment.metric_type
        selection_time      = 0
        
        ct = 0
        while ct < self.iterations:

            time.sleep(self.delay - self.delay_correction)

            print 'Controller delay:', self.delay_correction
            
                        
            if not self.manager_event == None:
                self.manager_event.wait()
                self.manager_event.clear()
                
            if (not self.controller_event == None) and self.controller_event.is_set():
                self.controller_event.clear()

            start_time = time.time()
            
            instances_number        = get_number_of_servers(self.environment)
            cores_number_by_server  = get_number_of_cores_by_server(self.environment)
            
            ct += 1
            print 'Controller: {0}'.format(ct)
            
            selection_time      += self.delay
            
            allocation          = (instances_number, cores_number_by_server)
            
            if there_is_violation(self.environment, metric_type) or is_selection_point(selection_time, self.environment.selection_peiodicity):
                selection_time  = 0
                self.predictor  = select_predictor(self.environment) 
                
            predictors_list = [ x for x in self.environment.predictor_type_list if (not x == self.predictor.NAME) and (not x == 'EN')]
            self.events  = run_predictions(self.environment, predictors_list)

            if self.predictor.NAME == 'EN':
                wait_for_all_events(self.events)
            
            prediction      = self.predictor.run()

            if not self.predictor.NAME == 'EN':
                en_predictor    = get_predictor_by_name(self.environment, 'EN', None)
                wait_for_all_events(self.events)
                en_predictor.start()
                
            capacity_value  = capacity_planning(self.environment, prediction, allocation)
            
            actuator = Actuator(self.environment, capacity_value)
            actuator.start()
            
            if not self.controller_event == None:
                self.controller_event.set()
                
            self.delay_correction   = time.time() - start_time
        
        return self.predictor.NAME