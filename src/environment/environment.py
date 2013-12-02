class Env(object):

    user_name           = ''
    project_id          = ''
    project_name        = ''
    user_password        = ''
    ip_base             = ''
    nova_port           = ''
    ceilometer_port        = ''
    keystone_port        = ''
    monitoring_period   = ''
    auth_token          = ''
    database_user       = ''
    database_password   = ''
    database_addr       = ''
    database_port       = ''
    database_database   = ''
    metric_list         = []
    billing_period      = ''
    control_periodicity = ''
    max_instance_num    = ''
    min_instance_num    = ''
    instance_type_list  = []
    instance_id_list    = []
    instance_cpu_list   = [] 
    predictor_type_list = []
    prediction_horizon  = ''
    reference_value     = ''
    

    def __init__(self, user_name, user_password, project_id, project_name, auth_token, ip_base, nova_port, ceilometer_port, keystone_port, monitoring_period, database_user, database_password, database_addr, database_port, database_database, metric_list, billing_period, control_periodicity, max_instance_num, min_instance_num, instance_type_list, instance_id_list, instance_cpu_list, image_id, predictor_type_list, prediction_horizon, reference_value):

            self.user_name                = user_name
            self.user_password          = user_password
            self.project_id             = project_id
            self.project_name           = project_name
            self.auth_token             = auth_token
            self.ip_base                = ip_base
            self.nova_port              = nova_port
            self.ceilometer_port        = ceilometer_port
            self.keystone_port          = keystone_port
            self.monitoring_period      = monitoring_period
            self.database_user          = database_user
            self.database_password      = database_password
            self.database_addr          = database_addr    
            self.database_port          = database_port
            self.database_database      = database_database
            self.metric_list            = metric_list
            self.billing_period         = billing_period
            self.control_periodicity    = control_periodicity
            self.max_instance_num       = max_instance_num
            self.min_instance_num       = min_instance_num
            self.instance_type_list     = instance_type_list
            self.instance_id_list       = instance_id_list
            self.instance_cpu_list       = instance_cpu_list
            self.image_id               = image_id
            self.predictor_type_list    = predictor_type_list
            self.prediction_horizon     = prediction_horizon
            self.reference_value        = reference_value
