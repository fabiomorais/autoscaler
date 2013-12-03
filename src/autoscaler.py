import sys
import time
import cStringIO
import pycurl

sys.path.append('../conf')
sys.path.append('controller')
sys.path.append('database')
sys.path.append('environment')
sys.path.append('manager')
sys.path.append('monitor')
sys.path.append('predictor')
sys.path.append('util')

import configuration
from configuration_helper import create_environment
from monitor import Monitor
from data_manager import Manager
from controller import Controller
from database_helper import init_database

def start_load_generator_server(service_ip, client_ip, port):

    url    = 'http://' + service_ip + ':' + port + '/update?ips=' + client_ip
    
    buf = cStringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buf.write)
    c.perform()

    buf.close()

if __name__ == '__main__':

    delay        = 30
    iterations     = 6 #float(sys.argv[1])
    env         = create_environment(configuration)
    
    init_database(env)
    
    #start_load_generator_server('150.165.85.149', '10.11.12.2', '5555')
    
    monitor     = Monitor(env, delay, iterations)
    manager     = Manager(env, delay, iterations, "2480e901-e945-4612-96fd-f4ec14d1e35f")
    #controller  = Controller(env, delay, iterations)
    
    #monitor.start()
    #time.sleep(1)
    #manager.start()
    #time.sleep(1)
    #controller.start()
    
    #monitor.join()
    #manager.join()
    #controller.join()