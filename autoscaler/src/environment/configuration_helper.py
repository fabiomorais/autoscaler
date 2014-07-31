
import subprocess
import re

from environment import * 

def constant(f):
	def fset(self, value):
		raise SyntaxError
	def fget(self):
		return f(self)
	return property(fget, fset)

class _Const(object):

	@constant
	def USER_NAME_PATTERN(self):
		return 'OS_USERNAME'
	
	@constant
	def IP_BASE_PATTERN(self):
		return 'OS_AUTH_URL'

	@constant
	def PROJECT_NAME_PATTERN(self):
		return 'OS_TENANT_NAME'

	@constant
	def PROJECT_ID_PATTERN(self):
		return 'OS_TENANT_ID'

def create_environment(configuration_file):

	nova_port				= configuration_file.NOVA_PORT
	keystone_port			= configuration_file.KEYSTONE_PORT
	ceilometer_port			= configuration_file.CEILOMETER_PORT
	user_password			= configuration_file.USER_PASSWORD
	openrc_file_path		= configuration_file.OPENSTACK_CONF_FILE
	monitoring_period		= configuration_file.MONITORING_PERIOD
	database_user			= configuration_file.DATABASE_USER
	database_password		= configuration_file.DATABASE_PASSWORD
	database_addr			= configuration_file.DATABASE_ADDR
	database_port			= configuration_file.DATABASE_PORT
	database_database		= configuration_file.DATABASE_DB_NAME
	metric_type				= configuration_file.METRIC_TYPE
	
	billing_period			= configuration_file.BILLING_PERIOD
	control_periodicity		= configuration_file.CONTROL_PERIODICITY
	selection_peiodicity	= configuration_file.SELECTION_PERIODICITY
	selection_data_length	= configuration_file.SELECTION_DATA_LENGTH
	max_instance_num		= configuration_file.MAX_INSTANCE_NUMBER
	min_instance_num		= configuration_file.MIN_INSTANCE_NUMBER
	instance_type			= configuration_file.FLAVOR_TYPE
	instance_id				= configuration_file.FLAVOR_ID
	image_id				= configuration_file.IMAGE_ID
	image_name				= configuration_file.IMAGE_NAME
	predictor_type_list		= get_predictor_type_list(configuration_file.PREDICTOR_TYPE)
	predictor_data_lenght	= get_predictor_data_lenght(configuration_file.PREDICTOR_DATA_LEN, predictor_type_list)
	prediction_horizon		= configuration_file.PREDICTION_HORIZON
	reference_value			= configuration_file.REFERENCE_VALUE
	violation_value			= configuration_file.VIOLATION_VALUE
	
	enable_floating_ip		= configuration_file.ENALBLE_FLOATING_IP
	floating_ip_list		= get_floating_ip_list(configuration_file.FLOATING_IP)
	load_generator_ip		= configuration_file.LOAD_GENERATOR_ADDR
	load_generator_port		= configuration_file.LOAD_GENERATOR_PORT
	
	user_name				= get_user_name(openrc_file_path)
	project_id				= get_project_id(openrc_file_path)
	project_name			= get_project_name(openrc_file_path)
	ip_base					= get_ip_base(openrc_file_path)
	auth_token				= get_auth_token(ip_base, keystone_port, user_name, user_password, project_id)
	
	is_cloud_prod			= configuration_file.CLOUD_PROD
	
	return Env(user_name, user_password, project_id, project_name, auth_token, ip_base, nova_port, 
			ceilometer_port, keystone_port, monitoring_period, database_user, database_password, 
			database_addr, database_port, database_database, metric_type, billing_period, 
			control_periodicity, selection_peiodicity, selection_data_length, max_instance_num, min_instance_num, 
			instance_type, instance_id, image_id, image_name, predictor_type_list, predictor_data_lenght,
			prediction_horizon, reference_value, violation_value, enable_floating_ip, floating_ip_list, load_generator_ip, load_generator_port, is_cloud_prod)

def get_project_id(configuration_file):
	CONST = _Const()
	return get_propertie(configuration_file, CONST.PROJECT_ID_PATTERN)

def get_metric_list(metric_list):
	return metric_list.split(';')

def get_predictor_type_list(predictor_type_list):
	return predictor_type_list.split(';')

def get_predictor_data_lenght(predictor_data_len_list, predictor_type_list):
	
	predictor_data_len_dict = {}
	data_len_list = predictor_data_len_list.split(';')
	for i in xrange(len(data_len_list)):
		predictor_data_len_dict[predictor_type_list[i]] = data_len_list[i]

	return predictor_data_len_dict

def get_floating_ip_list(floating_ip_list):
	return floating_ip_list.split(';')
	
def get_project_name(configuration_file):
	CONST 		= _Const()
	project_name 	= get_propertie(configuration_file, CONST.PROJECT_NAME_PATTERN)
	value_regex 	= re.compile("(?<=\")(?P<value>.*?)(?=\")")
	match 		= value_regex.search(project_name)
	return match.group('value')

def get_ip_base(configuration_file):
	CONST 		= _Const()
	url_base 	= get_propertie(configuration_file, CONST.IP_BASE_PATTERN)
	value_regex 	= re.compile("(?<=http://)(?P<value>.*?)(?=:)")
	match 		= value_regex.search(url_base)
	return match.group('value')

def get_user_name(configuration_file):

	CONST 		= _Const()
	user_name 	= get_propertie(configuration_file, CONST.USER_NAME_PATTERN)
	value_regex 	= re.compile("(?<=\")(?P<value>.*?)(?=\")")
	match 		= value_regex.search(user_name)
	
	return match.group('value')

def get_propertie(configuration_file, pattern):

	configuration_file 	= open(configuration_file)
	file_lines		= configuration_file.readlines()

	file_line	= filter(lambda x: pattern in x, file_lines)

	if(len(file_line) == 0):
		return ''

	value_regex 	= re.compile("(?<=" + pattern + "=)(?P<value>.*?)(?=\n)")
	match 		= value_regex.search(file_line[0])
	result 		= match.group('value')
	
	return result

def create_keystone_url(ip_base, keystone_port):
	return 'http://' + ip_base + ':' + keystone_port + '/v2.0'

def get_auth_token(ip_base, keystone_port, user_name, user_password, project_id):

	keystone_url	= create_keystone_url(ip_base, keystone_port)
	
	keystone_path	= 'keystone'
	keystone_list	= [keystone_path]
	
	keystone_list.append('--os-auth-url')
	keystone_list.append(keystone_url)

	keystone_list.append('--os-username')
	keystone_list.append(user_name)

	keystone_list.append('--os-password')
	keystone_list.append(user_password)

	keystone_list.append('--os-tenant-id')
	keystone_list.append(project_id)

	keystone_list.append('token-get')

	tk	 	= subprocess.Popen(keystone_list, stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]
	
	token_result    = tk.split('\n')
	
	return filter(lambda x: ' id ' in x, token_result)[0].split(' |')[1].strip()
