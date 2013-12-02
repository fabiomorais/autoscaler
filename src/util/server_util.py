import re
import json

from database_util import get_database_timestamp_format

def get_server_id(servers_data, index):
	
	server_id	= json.dumps(servers_data['servers'][index]['id'])
	value_regex 	= re.compile("(?<=\")(?P<value>.*?)(?=\")")
	match 		= value_regex.search(server_id)
	return match.group('value')

def get_data_server(server):
	return (str(server['id']), str(server['name']), (server['flavor']['id']), str(server['image']['id']), get_database_timestamp_format(str(server['created']), '%Y-%m-%dT%H:%M:%SZ'))
