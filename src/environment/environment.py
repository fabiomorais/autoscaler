class Env(object):

    user_name               = ''
    project_id              = ''
    project_name            = ''
    user_password           = ''
    ip_base                 = ''
    nova_port               = ''
    ceilometer_port         = ''
    keystone_port           = ''
    monitoring_period       = ''
    auth_token              = ''
    database_user           = ''
    database_password       = ''
    database_addr           = ''
    database_port           = ''
    database_database       = ''
    metric_type             = ''
    billing_period          = ''
    control_periodicity     = ''
    selection_peiodicity    = ''
    selection_data_length   = ''
    max_instance_num        = ''
    min_instance_num        = ''
    instance_type           = ''
    instance_vcpu           = None
    instance_id             = ''
    instance_name           = ''
    instance_ip_dict        = {}
    predictor_type_list     = []
    prediction_horizon      = ''
    reference_value         = ''
    violation_value         = ''
    image_id                = ''
    image_name              = ''
    floating_ip_list        = []
    enable_floating_ip      = None
    load_generator_ip       = ''
    load_generator_port     = ''
    is_cloud_prod           = None
    

    def __init__(self, user_name, user_password, project_id, project_name, 
                 auth_token, ip_base, nova_port, ceilometer_port, keystone_port, 
                 monitoring_period, database_user, database_password, database_addr, 
                 database_port, database_database, metric_type, billing_period, 
                 control_periodicity, selection_peiodicity, selection_data_length, 
                 max_instance_num, min_instance_num, instance_type, instance_id, 
                 image_id, image_name, predictor_type_list, 
                 prediction_horizon, reference_value, violation_value, enable_floating_ip, 
                 floating_ip_list, load_generator_ip, load_generator_port, is_cloud_prod):

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
            self.metric_type            = metric_type
            self.billing_period         = billing_period
            self.control_periodicity    = control_periodicity
            self.selection_peiodicity   = selection_peiodicity
            self.max_instance_num       = max_instance_num
            self.min_instance_num       = min_instance_num
            self.instance_type          = instance_type
            self.instance_id            = instance_id
            self.image_id               = image_id
            self.image_name             = image_name
            self.predictor_type_list    = predictor_type_list
            self.prediction_horizon     = prediction_horizon
            self.reference_value        = reference_value
            self.violation_value        = violation_value
            self.floating_ip_list       = floating_ip_list
            self.enable_floating_ip     = enable_floating_ip
            self.load_generator_ip      = load_generator_ip
            self.load_generator_port    = load_generator_port
            self.is_cloud_prod          = is_cloud_prod
            self.selection_data_length  = selection_data_length