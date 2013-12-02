import cStringIO
import pycurl
import json

def get_server_information_json(env, server_id):

	server_list_url	= get_server_information_url(env, server_id)

	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, server_list_url)
	c.setopt(c.HTTPHEADER, ['Accept: application/json', 'User-Agent: python-novaclient', 'X-Auth-Token: ' + env.auth_token])
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	json_data 	= buf.getvalue()
	buf.close()

	return json.loads(json_data)

def get_server_list_json(env):

	server_list_url	= get_server_list_url(env)

	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, server_list_url)
	c.setopt(c.HTTPHEADER, ['Accept: application/json', 'User-Agent: python-novaclient', 'X-Auth-Token: ' + env.auth_token])
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	json_data 	= buf.getvalue()
	buf.close()

	return json.loads(json_data)

def get_flavor_list_json(env):

	flavor_list_url	= get_flavor_list_url(env)

	
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, flavor_list_url)
	c.setopt(c.HTTPHEADER, ['Accept: application/json', 'User-Agent: python-novaclient', 'X-Auth-Token: ' + env.auth_token])
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	json_data 	= buf.getvalue()
	buf.close()

	return json.loads(json_data)

def get_image_list_json(env):

	flavor_list_url	= get_image_list_url(env)

	
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, flavor_list_url)
	c.setopt(c.HTTPHEADER, ['Accept: application/json', 'User-Agent: python-novaclient', 'X-Auth-Token: ' + env.auth_token])
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	json_data 	= buf.getvalue()
	buf.close()

	return json.loads(json_data)

def create_server(env, image_id, flavor_id, instance_name):

	create_server_url	= get_create_server_url(env)
	buf = cStringIO.StringIO()

	create_server_data	= get_create_server_data(instance_name, image_id, flavor_id)
	
	c = pycurl.Curl()
	c.setopt(c.CUSTOMREQUEST, 'POST')
	c.setopt(c.URL, create_server_url)
	c.setopt(c.HTTPHEADER, ['Content-type: application/json', 'Accept: application/json', 'User-Agent: python-novaclient', 'X-Auth-Token: ' + env.auth_token])
	c.setopt(c.POSTFIELDS, create_server_data)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()
	
	json_data 	= buf.getvalue()
	
	buf.close()

	return json.loads(json_data)

def add_floating_ip(env, server_id, floating_ip):

	add_floating_ip_url	= get_add_floating_ip_url(env, server_id)
	buf = cStringIO.StringIO()

	add_floating_ip_data	= get_add_floating_ip_data(floating_ip)
	
	c = pycurl.Curl()
	c.setopt(c.CUSTOMREQUEST, 'POST')
	c.setopt(c.URL, add_floating_ip_url)
	c.setopt(c.HTTPHEADER, ['Content-type: application/json', 'Accept: application/json', 'User-Agent: python-novaclient', 'X-Auth-Token: ' + env.auth_token])
	c.setopt(c.POSTFIELDS, add_floating_ip_data)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()
	
	buf.close()

def delete_server(env, server_id):

	remove_server_url	= get_remover_server_url(env, server_id)
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.CUSTOMREQUEST, 'DELETE')
	c.setopt(c.URL, remove_server_url)
	c.setopt(c.HTTPHEADER, ["User-Agent: python-novaclient", "Accept: application/json", 'X-Auth-Token: ' + env.auth_token])
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	buf.close()
	
def get_server_information_url(env, server_id):
	return 'http://' + env.ip_base + ':' + env.nova_port + '/v2/' + env.project_id + '/servers/' + str(server_id)

def get_server_list_url(env):
	return 'http://' + env.ip_base + ':' + env.nova_port + '/v2/' + env.project_id + '/servers/detail'

def get_flavor_list_url(env):
	return 'http://' + env.ip_base + ':' + env.nova_port + '/v2/' + env.project_id + '/flavors/detail'

def get_image_list_url(env):
	return 'http://' + env.ip_base + ':' + env.nova_port + '/v2/' + env.project_id + '/images/detail'

def get_create_server_url(env):
	return 'http://' + env.ip_base + ':' + env.nova_port + '/v2/' + env.project_id + '/servers'

def get_add_floating_ip_url(env, server_id):
	return 'http://' + env.ip_base + ':' + env.nova_port + '/v2/' + env.project_id + '/servers/' + str(server_id) + '/action'

def get_add_floating_ip_data(floating_ip):
	return "{\"addFloatingIp\": {\"address\": \"" + str(floating_ip) + "\"}}"

def get_create_server_data(instance_name, image_id, flavor_id):
	return "{\"server\": {\"name\": \"" + str(instance_name) + "\", \"imageRef\": \"" + str(image_id) + "\", \"flavorRef\": \"" + str(flavor_id) + "\", \"max_count\": 1, \"min_count\": 1}}"

def get_remover_server_url(env, server_id):
	return 'http://' + env.ip_base + ':' + env.nova_port + '/v2/' + env.project_id + '/servers/' + str(server_id)
