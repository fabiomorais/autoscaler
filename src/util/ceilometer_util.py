import cStringIO
import pycurl
import json

def get_meter_statistics(env, meter):

	metric_statistics_url	= get_metric_statistics_url(env, meter)
	
	buf	= cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, metric_statistics_url)
	c.setopt(c.HTTPHEADER, ['X-Auth-Token: ' + env.auth_token])
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	json_data 	= buf.getvalue()
	buf.close()

	return json.loads(json_data)

def get_metric_data(env, meter, server_id, monitoring_interval):

	metric_data_url	= get_metric_data_url(env, meter, server_id, monitoring_interval)
	
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, metric_data_url)
	c.setopt(c.HTTPHEADER, ['X-Auth-Token: ' + env.auth_token])
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	json_data 	= buf.getvalue()
	buf.close()

	return json.loads(json_data)

def get_metric_statistics_url(env, meter):	
	return 'http://' + env.ip_base + ':' + env.ceilometer_port + '/v2/meters/' + meter + '/statistics'

def get_metric_data_url(env, meter, server_id, monitoring_interval):
	return 'http://' + env.ip_base + ':' + env.ceilometer_port + '/v2/meters/' + meter + '?q.field=resource_id&q.op=eq&q.value=' + server_id + '&q.field=timestamp&q.op=gt&q.value=' + monitoring_interval[1]
