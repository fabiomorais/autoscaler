from predictor import LastWindow
from database_helper import insert_or_update_prediction

def select_predictor(environment):
    predictor_name  = environment.predictor_type_list[0]
    
    if(predictor_name == 'LW'):
        return LastWindow(environment)
    
    return ''

def persist_prediction(environment, prediction):
    insert_or_update_prediction(environment, prediction)