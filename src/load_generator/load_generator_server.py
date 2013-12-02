import threading as t
import cStringIO
import pycurl
import time
import sys
import csv
import logging
import os

from flask import Flask, request
from collections import deque

app      = Flask(__name__)		
QUEUE    = deque()

log_file_path = str(os.getcwd() + '/log/generator_server.log')

logging.basicConfig(filename=log_file_path,level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger('generator_server')

def get_ips_list():
	return QUEUE.popleft()

def update_ips_list(ips_list):
	QUEUE.appendleft(ips_list)

def is_ips_list_available():
	return bool(QUEUE)

def get_put_load_url(ip, cpu_util):
	return 'http://' + ip + ':5555/level?cpu_util=' + str(cpu_util)

def send_load(ip, cpu_util):
	
	url	= get_put_load_url(ip, cpu_util)
	
	buf = cStringIO.StringIO()

	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, buf.write)
	c.perform()

	buf.close()

def get_metric_value(metric_type, file_name): 

	csvfile  = open(file_name, "rb")
	csv_file = csv.reader(csvfile, delimiter=' ')

	rownum    = 0
	col_index = 0
	col_name  = str(metric_type).upper()
	
	for row in csv_file:

		cpu_util = 0
    		if rownum == 0:
				header = row
				col_index = header.index(col_name)
    		else:
				yield 	row[col_index]

		rownum += 1

def generate_load(ips_list, metric_util, metric_type):
	
	for ip in ips_list:
		send_load(ip, metric_util)
		logger.info(metric_type + ': ' + str(metric_util) + ' -> ' + ip)

@app.route('/update')
def update_ips():
	
	ips_list = str(request.args.get('ips')).split(';')
	update_ips_list(ips_list)
	
	return "Updated"

class CPULoaderServer(t.Thread):

	delay        = None
	periodicy    = None
	process      = None
	metric_yield = None
	metric_type  = None
	metric_file  = None
	is_active    = None
	ips_list     = []

	def __init__(self, periodicy, metric_type, metric_file, error):
		t.Thread.__init__(self)

		self.delay   	  = 1
		self.periodicy    = periodicy
		self.metric_type  = metric_type
		self.metric_file  = metric_file
		self.metric_yield = get_metric_value(self.metric_type, self.metric_file)
		self.is_active    = True
		self.error		  = error

	def run(self):

		while self.is_active: 
			
			time.sleep(self.delay)

			if is_ips_list_available():
				self.ips_list = list(get_ips_list())
				self.delay = self.periodicy
			
			if len(self.ips_list) > 0:
				
				cpu_util = next(self.metric_yield, None)
				
				if cpu_util != None:
					cpu_util_str = str(min(100, max((float(cpu_util) - self.error), self.error)))
					#cpu_util_str = str(round(min(100, max(float(cpu_util), 1)), 0))
					generate_load(self.ips_list, cpu_util_str, self.metric_type)
				else:
					logger.warning('No more metric values')
					self.is_active = False

if __name__ == '__main__':
	
	metric_file = str(sys.argv[1])
	delay	    = int(sys.argv[2])
	metric_type = str(sys.argv[3])
	error 		= float(sys.argv[4])
	port_addr	= str(sys.argv[5])
	
	cpu_loader = CPULoaderServer(delay, metric_type, metric_file, error)
	cpu_loader.start()

	app.run('0.0.0.0', port=port_addr)	
