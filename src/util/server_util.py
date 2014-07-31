import re
import json

from database_util import get_database_timestamp_format

def get_server_id(servers_data, index):
	
	server_id	= json.dumps(servers_data['servers'][index]['id'])
	value_regex 	= re.compile("(?<=\")(?P<value>.*?)(?=\")")
	match 		= value_regex.search(server_id)
	return match.group('value')

def get_server_ip(env, servers_data):
	
	if len(servers_data['server']['addresses']) == 0:
		return None
	
	if env.is_cloud_prod:
		return str(servers_data['server']['addresses']['semi-private-network'][0]['addr'])
	return str(servers_data['server']['addresses']['private'][0]['addr'])

def get_data_server(server):
	return (str(server['id']), str(server['name']), (server['flavor']['id']), str(server['image']['id']), get_database_timestamp_format(str(server['created']), '%Y-%m-%dT%H:%M:%SZ'))
