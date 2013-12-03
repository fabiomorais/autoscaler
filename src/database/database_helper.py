import mysql.connector

from flavor_util import *
from server_util import get_data_server
from database_util import get_database_timestamp_format

def delete_tables(cursor):
	
	TABLES = []
	TABLES.append("DROP TABLE IF EXISTS metric_usage")
	TABLES.append("DROP TABLE IF EXISTS metric_prediction")
	TABLES.append("DROP TABLE IF EXISTS vm")
	TABLES.append("DROP TABLE IF EXISTS project")
	TABLES.append("DROP TABLE IF EXISTS flavor")
	
	for x in range(0, len(TABLES)):
		cursor.execute(TABLES[x])

def create_tables(cursor):

	TABLES = []
	TABLES.append(
	"CREATE TABLE `project` ("
	"`ID` VARCHAR(255) NOT NULL,"
	"`NAME` VARCHAR(255),"
	"PRIMARY KEY (`ID`)"
	")")

	TABLES.append(
	"CREATE TABLE `flavor` ("
	"`ID` VARCHAR(255) NOT NULL,"
	"`NAME` VARCHAR(255),"
	"`VCPUS` FLOAT,"
	"`RAM` FLOAT,"
	"`DISK` FLOAT,"
	"PRIMARY KEY (`ID`)"
	")")

	TABLES.append(
	"CREATE TABLE `vm` ("
	"`ID` VARCHAR(255) NOT NULL,"
	"`NAME` VARCHAR(255),"
	"`IMAGE_ID` VARCHAR(255),"
	"`FLAVOR_ID` VARCHAR(255),"
	"`CREATION_DATE` TIMESTAMP,"
	"PRIMARY KEY (`ID`)," 
	"CONSTRAINT `vm_ibfk_1` FOREIGN KEY (`FLAVOR_ID`) REFERENCES `flavor`(`ID`) ON DELETE CASCADE"
	")")

	
	TABLES.append(
	"CREATE TABLE `metric_usage` ("
	"`ID` INT NOT NULL AUTO_INCREMENT,"
	"`TIME` TIMESTAMP,"
	"`VM_ID` VARCHAR(255),"
	"`PROJECT_ID` VARCHAR(255),"
	"`UTIL` FLOAT," 
	"`TYPE` VARCHAR(255),"
	"PRIMARY KEY (`ID`),"
	"CONSTRAINT `metric_usage_ibfk_1` FOREIGN KEY (`VM_ID`) REFERENCES `vm`(`ID`) ON DELETE CASCADE,"
	"CONSTRAINT `metric_usage_ibfk_2` FOREIGN KEY (`PROJECT_ID`) REFERENCES `project`(`ID`) ON DELETE CASCADE"
	")")	
	
	TABLES.append(
	"CREATE TABLE `metric_prediction` ("
	"`ID` INT NOT NULL AUTO_INCREMENT,"
	"`TIME` TIMESTAMP,"
	"`PROJECT_ID` VARCHAR(255),"
	"`UTIL_PERCENT` FLOAT,"
	"`UTIL` FLOAT,"
	"`ALLOC` FLOAT," 
	"`TYPE` VARCHAR(255),"
	"`PREDICTOR` VARCHAR(255),"
	"PRIMARY KEY (`ID`),"
	"CONSTRAINT `metric_prediction_ibfk_1` FOREIGN KEY (`PROJECT_ID`) REFERENCES `project`(`ID`) ON DELETE CASCADE"
	")")	
		
	for x in range(0, len(TABLES)):
		cursor.execute(TABLES[x])

def init_database(env):

	cnx = mysql.connector.connect(user=env.database_user, password=env.database_password, host=env.database_addr, database=env.database_database, port=env.database_port)
	cursor = cnx.cursor()

	delete_tables(cursor)
	create_tables(cursor)
	
	cnx.commit()
	cnx.close()

def get_project_insert_structure():

	add_project = ("INSERT INTO project (ID, NAME) VALUES (\"{0}\", \"{1}\")")
	return add_project

def get_flavor_insert_or_update_structure():

	add_flavor = ("INSERT INTO flavor (ID, NAME, VCPUS, RAM, DISK) VALUES (\"{0}\", \"{1}\", {2}, {3}, {4}) ON DUPLICATE KEY UPDATE NAME = \"{1}\", VCPUS = {2}, RAM = {3}, DISK = {4}")
	return add_flavor

def get_server_insert_or_update_structure():

	add_server = ("INSERT INTO vm (ID, NAME, IMAGE_ID, FLAVOR_ID, CREATION_DATE) SELECT \"{0}\", \"{1}\", \"{3}\", \"{2}\", \"{4}\" ON DUPLICATE KEY UPDATE NAME = \"{1}\", IMAGE_ID = \"{3}\", FLAVOR_ID = \"{2}\"")
	return add_server

def get_metric_usage_insert_structure():

	add_metric_usage = ("INSERT INTO metric_usage (TIME, VM_ID, PROJECT_ID, UTIL, TYPE) SELECT \"{0}\", v.ID, p.ID, {3}, \"{4}\" FROM project AS p, vm AS v WHERE v.ID = \"{1}\" AND p.ID= \"{2}\"")
	return add_metric_usage

def get_server_update_structure():

	update_server = ("UPDATE vm SET INSTANCE_NAME = , IMAGE_ID, FLAVOR_ID) SELECT \"{0}\", \"{1}\", \"{3}\", ID FROM flavor WHERE FLAVOR_ID = \"{2}\"")
	return update_server

#def get_metric_create_or_update_view_structure():
#	create_view = ("CREATE OR REPLACE VIEW utilization AS SELECT c.TIME, c.PROJECT_ID, c.UTIL AS UTIL_PERCENT, (c.UTIL * SUM(f.VCPUS) / 100) AS UTIL , SUM(f.VCPUS) AS ALLOC, \"{2}\" AS TYPE FROM utilization_average AS c, vm AS v, flavor AS f WHERE c.TYPE = \"{2}\" AND v.FLAVOR_ID = f.ID GROUP BY c.TIME")
#	
#	return create_view

def get_metric_mean_create_or_update_view_structure_by_project():
	create_view = ("CREATE OR REPLACE VIEW utilization_average AS SELECT MIN(a.TIME) AS TIME, a.PROJECT_ID, AVG(a.UTIL) AS UTIL , \"{2}\" AS TYPE FROM metric_usage AS a, metric_usage AS b WHERE a.TYPE = \"{2}\" AND b.TYPE = \"{2}\" AND a.PROJECT_ID = \"{0}\" AND b.TIME = (SELECT MAX(TIME) as max from metric_usage) GROUP BY (UNIX_TIMESTAMP(a.TIME) - (UNIX_TIMESTAMP(b.TIME) MOD 300 + 1)) DIV 300")
	
	return create_view

def get_metric_mean_create_or_update_view_structure_by_server():
	create_view = ("CREATE OR REPLACE VIEW utilization_average AS SELECT MIN(a.TIME) AS TIME, a.VM_ID, a.PROJECT_ID, AVG(a.UTIL) AS UTIL , \"{2}\" AS TYPE FROM metric_usage AS a, metric_usage AS b WHERE a.VM_ID = \"{3}\" AND b.VM_ID = \"{3}\" AND a.TYPE = \"{2}\" AND b.TYPE = \"{2}\" AND a.PROJECT_ID = \"{0}\" AND b.PROJECT_ID = \"{0}\" AND b.TIME = (SELECT MAX(TIME) as max from metric_usage) GROUP BY a.VM_ID, ((UNIX_TIMESTAMP(a.TIME) - (UNIX_TIMESTAMP(b.TIME) MOD 300 + 1)) DIV 300)")
	
	return create_view

def get_uptime_create_or_update_view_structure():
	create_view = ("CREATE OR REPLACE VIEW vm_uptime AS SELECT ID as VM_ID, ABS(TIMESTAMPDIFF(hour, CREATION_DATE, \'{1}\')) AS HOUR, ABS(TIMESTAMPDIFF(minute, CREATION_DATE, \'{1}\')) AS MINUTE, ABS(TIMESTAMPDIFF(second, CREATION_DATE, \'{1}\')) AS SECOND, \'{1}\' AS TIME FROM vm")
	return create_view

def get_history_data_structure():
	select_data = ("SELECT TIME, UTIL_PERCENT, UTIL, ALLOC, TYPE FROM utilization WHERE PROJECT_ID = \"{0}\" AND TYPE = \"{2}\" ORDER BY TIME DESC LIMIT {1}")
	return select_data

def get_vms_avalable_for_deletion_structure():
	uptime_data = ("SELECT * FROM vm_uptime WHERE ((MINUTE + ( {0}/60 )) MOD ({1}/60)) = 0 ORDER BY SECOND DESC LIMIT {2}")
	return uptime_data
	
def get_prediction_insert_structure():
	add_prediction	= ("INSERT INTO metric_prediction (TIME, PROJECT_ID, UTIL_PERCENT, UTIL, ALLOC, TYPE, PREDICTOR) VALUES (\"{1}\", \"{0}\", {2}, {3}, {4}, \"{5}\", \"{6}\")")
	return add_prediction

def get_metric_history_by_project_structure():
	metric_history = ("SELECT CONVERT_TZ(TIME,'+00:00','-03:00') as TIMESTAMP, UTIL FROM utilization_average WHERE TYPE = \"{1}\" AND PROJECT_ID = \"{0}\"")
	return metric_history

def get_metric_history_by_server_structure():
	metric_history = ("SELECT CONVERT_TZ(TIME,'+00:00','-03:00') as TIMESTAMP, UTIL, VM_ID FROM utilization_average WHERE TYPE = \"{1}\" AND PROJECT_ID = \"{0}\" AND VM_ID = \"{2}\"")
	return metric_history
	
def execute_creation_command(env, command_structure, command_data_values):

	command	= command_structure.format(*command_data_values)

	cnx = mysql.connector.connect(user=env.database_user, password=env.database_password, host=env.database_addr, database=env.database_database, port=env.database_port)

	cursor 	= cnx.cursor()
	cursor.execute(command)
	
	cnx.commit()
	
	cursor.close()
	cnx.close()
	
def execute_selection_command(env, command_structure, command_data_values):

	command	= command_structure.format(*command_data_values)

	cnx = mysql.connector.connect(user=env.database_user, password=env.database_password, host=env.database_addr, database=env.database_database, port=env.database_port)
	
	cursor 	= cnx.cursor()
	cursor.execute(command)

	result	= []
		
	for line in cursor:
		result.append(line)

	cursor.close()
	cnx.close()
	
	return result

def insert_project(env, project_id, project_name):
	
	insert_structure 	= get_project_insert_structure()
	insert_data_values	= (project_id, project_name)

	execute_creation_command(env, insert_structure, insert_data_values)

def insert_or_update_flavor(env, flavor):
	
	structure 	= get_flavor_insert_or_update_structure()
	data_values	= get_data_flavor(flavor)

	execute_creation_command(env, structure, data_values)

def insert_or_update_server(env, server):
	
	structure 	= get_server_insert_or_update_structure()
	data_values	= get_data_server(server)

	execute_creation_command(env, structure, data_values)

def insert_metric_usage(env, metric_type, server_id, project_id, timestamp, metric_util):

	insert_structure 	= get_metric_usage_insert_structure()
	insert_data_values	= (timestamp, server_id, project_id, metric_util, metric_type)

	execute_creation_command(env, insert_structure, insert_data_values)
	
def insert_or_update_flavors(env, flavors):
	for x in range(0, len(flavors['flavors'])):
		insert_or_update_flavor(env, flavors['flavors'][x])

def insert_or_update_servers(env, servers):
	for x in range(0, len(servers['servers'])):
		insert_or_update_server(env, servers['servers'][x])

def create_or_update_metric_average_view_by_server(env, metric_type, monitoring_interval, server_id):
	
	structure 	= get_metric_mean_create_or_update_view_structure_by_server()
	data_values	= (env.project_id, monitoring_interval[0], metric_type, server_id)

	execute_creation_command(env, structure, data_values)
	
def create_or_update_metric_average_view_by_project(env, metric_type, monitoring_interval):
	
	structure 	= get_metric_mean_create_or_update_view_structure_by_project()
	data_values	= (env.project_id, monitoring_interval[0], metric_type)

	execute_creation_command(env, structure, data_values)

def create_or_update_uptime_vm_view(env, monitoring_interval):
	
	structure 	= get_uptime_create_or_update_view_structure()
	data_values	= (env.project_id, get_database_timestamp_format(monitoring_interval[0], '%Y-%m-%dT%H:%M:%S'), )

	execute_creation_command(env, structure, data_values)	
	
def create_or_update_metric_view(env, metric_type, monitoring_interval):
	
	structure 	= get_metric_create_or_update_view_structure()
	data_values	= (env.project_id, monitoring_interval[0], metric_type)

	execute_creation_command(env, structure, data_values)
	
def get_history_data(env, data_length, metric_type):
	
	structure	= get_history_data_structure()
	data_values = (env.project_id, str(data_length), metric_type)
	
	return execute_selection_command(env, structure, data_values)

def get_vms_avalable_for_deletion_data(env, capacity_limit):
	
	structure	= get_vms_avalable_for_deletion_structure()
	data_values = (env.control_periodicity, env.billing_period, capacity_limit)
	
	return execute_selection_command(env, structure, data_values)

def insert_or_update_prediction(env, prediction):
	
	structure	= get_prediction_insert_structure()
	data_values	= prediction
	
	execute_creation_command(env, structure, data_values)
	
def get_metric_history_by_server(env, metric_type, server_id):
	
	structure   = get_metric_history_by_server_structure()
	data_values	= (env.project_id, metric_type, server_id)
	
	
	return execute_selection_command(env, structure, data_values)

def get_metric_history_by_project(env, metric_type):
	
	structure   = get_metric_history_by_project_structure()
	data_values	= (env.project_id, metric_type)
	
	
	return execute_selection_command(env, structure, data_values)