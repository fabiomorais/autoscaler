import threading as t
import time

from predictor_helper import select_predictor
from predictor_helper import persist_prediction
from capacity_planner import capacity_planning
from actuator import actuate_on_system

class Controller(t.Thread):
    
    def __init__(self, env, delay, iterations=1):

        t.Thread.__init__(self)
        
        self.delay          = delay
        self.iterations     = iterations
        self.environment    = env
    
    def run(self):

        predictor   = select_predictor(self.environment) 

        ct = 0
        while ct < self.iterations:

            ct += 1
            print 'Controller: {0}'.format(ct)
            
            metric_list         = self.environment.metric_list

            for x in range(0, len(metric_list)):
                
                metric_type     = metric_list[x]
                prediction      = predictor.predict(metric_type)
                capacity_value  = capacity_planning(self.environment, prediction, metric_type)
            
                print capacity_value
                
                actuate_on_system(self.environment, capacity_value)

                persist_prediction(self.environment, prediction)

            time.sleep(self.delay)