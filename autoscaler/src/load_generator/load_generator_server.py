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

app      	= Flask(__name__)		
QUEUE    	= deque()
abort_flag	= False

log_file_path = str(os.getcwd() + '/../log/generator_server.log')

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

'''
def send_load(ip, cpu_util, metric_type):
	
	url			= get_put_load_url(ip, cpu_util)
	abort_flag	= False
	
	while not abort_flag:

		buf = cStringIO.StringIO()
	
		c = pycurl.Curl()
		c.setopt(c.URL, url)
		c.setopt(c.WRITEFUNCTION, buf.write)

		try:
			logger.info('Trying to send load to ' + url)
			c.perform()
			
			logger.info(metric_type + ': ' + str(cpu_util) + ' -> ' + ip)
			abort_flag	= True
		except pycurl.error, error:
			errstr = error[1]

			logger.warning('An error occurred: ' +  errstr)
			abort_flag	= False
			
			time.sleep(5)
		finally:
			buf.close()
			logger.warning('Finally')
'''

class Sender(t.Thread):

	delay        = None
	periodicy    = None
	process      = None
	metric_yield = None
	metric_type  = None
	metric_file  = None
	is_active    = None
	ips_list     = []

	def __init__(self, ip, cpu_util, metric_type):
		t.Thread.__init__(self)
		
		self.ip				= ip
		self.cpu_util		= cpu_util
		self.metric_type	= metric_type
		self.abort_flag		= False

	def run(self):
		
		url			= get_put_load_url(self.ip, self.cpu_util)
		
		while not self.abort_flag:
	
			buf = cStringIO.StringIO()
		
			c = pycurl.Curl()
			c.setopt(c.URL, url)
			c.setopt(c.WRITEFUNCTION, buf.write)
	
			try:
				logger.info('Trying to send load to ' + url)
				c.perform()
				
				logger.info(metric_type + ': ' + str(self.cpu_util) + ' -> ' + self.ip)
				self.abort_flag	= True
			except pycurl.error, error:
				errstr = error[1]
	
				logger.warning('An error occurred: ' +  errstr)
				self.abort_flag	= False
				
				time.sleep(5)
			finally:
				buf.close()
				

def get_metric_value(metric_type, file_name): 

	csvfile  = open(file_name, "rb")
	csv_file = csv.reader(csvfile, delimiter=' ')

	rownum    = 0
	col_index = 0
	col_name  = str(metric_type).upper()
	
	for row in csv_file:

		if rownum == 0:
			header = row
			col_index = header.index(col_name)
		else:
			yield 	row[col_index]

		rownum += 1

def generate_load(ips_list, metric_util, metric_type, old_serders):

	for threads in old_serders:
		threads.abort_flag	= True
		
	senders = []
	
	for ip in ips_list:
		sender = Sender(ip, metric_util, metric_type)
		senders.append(sender)
		sender.start()
		
	return senders

@app.route('/update')
def update_ips():
	
	tmp_list = str(request.args.get('ips')).split(';')

	ips_list = [ x for x in tmp_list if not x == '']
	ips_list = sorted(ips_list)
	
	update_ips_list(ips_list)
	
	return "Updated"

@app.route('/test')
def test():
	return "Test"

class CPULoaderServer(t.Thread):

	delay        = None
	periodicy    = None
	process      = None
	metric_yield = None
	metric_type  = None
	metric_file  = None
	is_active    = None
	ips_list     = []
	senders		 = []

	def __init__(self, periodicy, metric_type, metric_file, error, vcpus):
		t.Thread.__init__(self)

		self.delay   	  = 1
		self.periodicy    = periodicy
		self.metric_type  = metric_type
		self.metric_file  = metric_file
		self.metric_yield = get_metric_value(self.metric_type, self.metric_file)
		self.is_active    = True
		self.error		  = error
		self.vcpus        = vcpus

	def run(self):

		while self.is_active: 
			
			time.sleep(self.delay)

			if is_ips_list_available():
				self.ips_list = list(get_ips_list())
				self.delay = self.periodicy
			
			if len(self.ips_list) > 0:
				
				metric_util = next(self.metric_yield, None)
				
				
				if metric_util != None:
					
					metric_util 	= float(metric_util) / (len(self.ips_list) * int(self.vcpus)) * 100
					metric_util_str = str(min(95, max((float(metric_util) - self.error), self.error)))

					tmp_senders		= generate_load(self.ips_list, metric_util_str, self.metric_type, self.senders)
					self.senders 	= tmp_senders
				
				else:
					self.is_active = False
					logger.info('No more metric values')

if __name__ == '__main__':
	
	metric_file = str(sys.argv[1])
	delay	    = int(sys.argv[2])
	metric_type = str(sys.argv[3])
	error 		= float(sys.argv[4])
	vcpus		= int(sys.argv[5])
	port_addr	= str(sys.argv[6])
	
	cpu_loader = CPULoaderServer(delay, metric_type, metric_file, error, vcpus)
	cpu_loader.start()

	#Disable flask log
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.ERROR)

	app.run('0.0.0.0', port=port_addr)	
