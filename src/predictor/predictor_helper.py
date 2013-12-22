import time

from predictor import LastWindow, AutoCorrelation, LinearRegression, AutoRegression, ARIMA, Ensemble
from database_helper import get_history_data, get_prediction_history_by_predictor
from capacity_planner import capacity_value


def select_predictor(env):
    
    return get_predictor_by_name(env, 'EN')

    current_time            = time.time()
    metric_history          = get_history_data(env, env.selection_data_length, env.metric_type)
    pattern                 = '%Y-%m-%d %H:%M:%S'
    timestamp               = time.strftime(pattern, time.gmtime(current_time))
    prediction_list         = []
    prediction_violations   = {}
    prediction_cost         = {}
    
    for predictor in env.predictor_type_list:

            prediction_hystory = get_prediction_history_by_predictor(env, predictor, env.metric_type, timestamp, env.selection_data_length)
            prediction_list.append(prediction_hystory)
    
    for p in range(0, len(prediction_list)):
    
        prediction_violations[env.predictor_type_list[p]]   = 0
        prediction_cost[env.predictor_type_list[p]]         = 0
        
        for m in range(0, len(metric_history)):
        
            metric_value    = metric_history[m][2]
            
            pred_value      = prediction_list[p][m][3]
            capacity_pred   = capacity_value(env, pred_value, env.instance_vcpu)

            is_violation    = (metric_value / capacity_pred) > env.violation_value
            cost            = capacity_pred
            
            prediction_violations[env.predictor_type_list[p]]   += int(is_violation)
            prediction_cost[env.predictor_type_list[p]]         += cost
    
    violation_reference     = min(prediction_violations.values())
    predictor_violation     = []

    for predictor in env.predictor_type_list:
        
        if (prediction_violations[predictor] == violation_reference):
                predictor_violation.append(predictor)
        else:
                del prediction_cost[predictor]

    cost_reference          = min(prediction_cost.values())
    predictors_cost         = []    

    for predictor in predictor_violation:
        if (prediction_cost[predictor] == cost_reference):
                predictors_cost.append(predictor)
                
    predictor_selection     = predictors_cost[0]
    print 'Selected predictor: ' + str(predictor_selection)
    
    return get_predictor_by_name(env, predictor_selection)
    
def get_predictor_by_name(env, predictor_name):
    
    if predictor_name == 'LW':
        return LastWindow(env, env.metric_type)
    elif predictor_name == 'AC':
        return AutoCorrelation(env, env.metric_type)
    elif predictor_name == 'LR':
        return LinearRegression(env, env.metric_type)
    elif predictor_name == 'AR':
        return AutoRegression(env, env.metric_type)
    elif predictor_name == 'ARIMA':
        return ARIMA(env, env.metric_type)
    elif predictor_name == 'EN':
        return Ensemble(env, env.metric_type)
    return None

