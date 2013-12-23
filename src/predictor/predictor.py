import subprocess
import json
import time
import datetime as d
import threading as t

from database_helper import get_history_data
from database_helper import insert_or_update_prediction
from database_helper import get_weight_history_data
from database_helper import get_prediction_history

def persist_prediction(environment, prediction):
    insert_or_update_prediction(environment, prediction)
    
def execute_prediction(env, history_json, predictor_name, num_period, pred_base_json, pred_json, weight_json):
    
    control_periodicity = env.control_periodicity
    prediction_horizon  = env.prediction_horizon
    
    command = []
    command.append('Rscript')
    command.append('../src/predictor/general_predictor.R')
    command.append(str(predictor_name))
    command.append(str(history_json))
    command.append(str(control_periodicity))
    command.append(str(prediction_horizon))
    command.append(str(num_period))
    command.append(str(pred_base_json))
    command.append(str(pred_json))
    command.append(str(weight_json))
        
    result, error = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()

    print error
    print result
    
    data_object     = json.loads(result)
    
    return data_object
    
    
def prepare_prediction_data(env, data_length, metric_type, predictor_name):
    
    history_data        = get_history_data(env, data_length, metric_type)
    
    history   = []
    for l in range(0,len(history_data)):
        timestamp = (history_data[l][0] - d.datetime(1970,1,1)).total_seconds()
        history.append((timestamp, history_data[l][1], history_data[l][2], history_data[l][3]))

    history_json = json.dumps(history)
    
    weight    = []
    pred      = []
    pred_base = []
    
    if predictor_name == 'EN':
        weight_data     = get_weight_history_data(env, data_length * (len(env.predictor_type_list) - 1))
        
        for l in range(0,len(weight_data)):
            timestamp = (weight_data[l][0] - d.datetime(1970,1,1)).total_seconds()
            weight.append((timestamp, weight_data[l][1], weight_data[l][2]))
            
        current_time            = time.time()
        pattern                 = '%Y-%m-%d %H:%M:%S'
        timestamp               = time.strftime(pattern, time.gmtime(current_time))
    
        pred_data               = get_prediction_history(env, metric_type, timestamp, data_length * (len(env.predictor_type_list)))
        
        timestamp_base          = time.strftime(pattern, time.gmtime(current_time + env.prediction_horizon))
            
        pred_base_data  = get_prediction_history(env, metric_type, timestamp_base, data_length * (len(env.predictor_type_list)))
        
        for l in range(0,len(pred_data)):
            timestamp = (pred_data[l][1] - d.datetime(1970,1,1)).total_seconds()
            pred.append((timestamp, pred_data[l][3], pred_data[l][5]))
        
            timestamp = (pred_base_data[l][1] - d.datetime(1970,1,1)).total_seconds()
            pred_base.append((timestamp, pred_base_data[l][3], pred_base_data[l][5]))
            
    pred_json       = json.dumps(pred)  
    pred_base_json  = json.dumps(pred_base)   
    weight_json     = json.dumps(weight)
    
    return history_json, weight_json, pred_json, pred_base_json
    
def _predict(env, metric_type, data_length, predictor_name, num_period):
        
    history_json, weight_json, pred_json, pred_base_json = prepare_prediction_data(env, data_length, metric_type, predictor_name) 
    
    prediction_json         = execute_prediction(env, history_json, predictor_name, num_period, pred_base_json, pred_json, weight_json)
        
    timestamp_pred          = prediction_json[0]['TIMESTAMP']
    metric_pred             = prediction_json[0]['CPU_UTIL']
        
    pattern                 = '%Y-%m-%d %H:%M:%S'
    timestamp_prediction    = time.strftime(pattern, time.gmtime(timestamp_pred))
       
    prediction              = (env.project_id, timestamp_prediction, metric_pred, str(metric_type).upper(), predictor_name)
        
    persist_prediction(env, prediction)
        
    return prediction

class LastWindow(t.Thread):

    DATA_LENGTH     = 1
    NAME            = 'LW'
    NUM_PERIOD      = 0
    
    def __init__(self, env, metric_type):
        
        t.Thread.__init__(self)
        self.environment    = env
        self.metric_type    = metric_type
    
    def run(self):
        return _predict(self.environment, self.metric_type, self.DATA_LENGTH, self.NAME, self.NUM_PERIOD)
    
class LinearRegression(t.Thread):
    
    DATA_LENGTH     = 10
    NAME            = 'LR'
    NUM_PERIOD      = 0
    
    def __init__(self, env, metric_type):
        
        t.Thread.__init__(self)
        self.environment    = env
        self.metric_type    = metric_type
        
    def run(self):
        return _predict(self.environment, self.metric_type, self.DATA_LENGTH, self.NAME, self.NUM_PERIOD)
    
class AutoCorrelation(t.Thread):
    
    DATA_LENGTH     = 10
    NAME            = 'AC'
    NUM_PERIOD      = 0
    
    def __init__(self, env, metric_type):

        t.Thread.__init__(self)
        self.environment    = env
        self.metric_type    = metric_type
        
    def run(self):
        return _predict(self.environment, self.metric_type, self.DATA_LENGTH, self.NAME, self.NUM_PERIOD)
        
        
class AutoRegression(t.Thread):
    
    DATA_LENGTH     = 10
    NAME            = 'AR'
    NUM_PERIOD      = 10
    
    def __init__(self, env, metric_type):

        t.Thread.__init__(self)
        self.environment    = env
        self.metric_type    = metric_type
        
    def run(self):
        return _predict(self.environment, self.metric_type, self.DATA_LENGTH, self.NAME, self.NUM_PERIOD)

class ARIMA(t.Thread):
    
    DATA_LENGTH     = 10
    NAME            = 'ARIMA'
    NUM_PERIOD      = 10
    
    def __init__(self, env, metric_type):

        t.Thread.__init__(self)
        self.environment    = env
        self.metric_type    = metric_type
        
    def run(self):
        return _predict(self.environment, self.metric_type, self.DATA_LENGTH, self.NAME, self.NUM_PERIOD)
    
class Ensemble(t.Thread):
    
    DATA_LENGTH     = 1
    NAME            = 'EN'
    NUM_PERIOD      = 0
    
    def __init__(self, env, metric_type):

        t.Thread.__init__(self)
        self.environment    = env
        self.metric_type    = metric_type
        
    def run(self):
        return _predict(self.environment, self.metric_type, self.DATA_LENGTH, self.NAME, self.NUM_PERIOD)