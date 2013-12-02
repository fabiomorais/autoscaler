from database_helper import get_history_data
import time
from datetime import datetime

class LastWindow():

    DATA_LENGTH     = 1
    NAME            = 'LW'
    
    def __init__(self, env):

        self.environment    = env
        
    def predict(self, metric_type):
        
        pattern         = '%Y-%m-%d %H:%M:%S'
        history_data    = get_history_data(self.environment, self.DATA_LENGTH, metric_type)
        
        timestamp_date          = datetime.strptime(str(history_data[0][0]), pattern)
        timestamp_epoch         = time.mktime(timestamp_date.timetuple())
        
        timestamp_prediction    = datetime.fromtimestamp(timestamp_epoch +  float(self.environment.prediction_horizon)).strftime(pattern)

        return (self.environment.project_id, timestamp_prediction, history_data[0][1], history_data[0][2], history_data[0][3], str(history_data[0][4]), self.NAME)
        
class LinearRegression():
    
    def __init__(self, env):

        self.environment    = env
        
    def predict(self):
        print ''
        
    