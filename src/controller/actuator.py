from nova_util import create_server
from nova_util import delete_server
from nova_util import get_server_ip_address
from nova_util import add_floating_ip
from database_helper import delete_server_by_id
from actuator_helper import select_vms_available_for_deletion

import threading as t
import time
import cStringIO
import pycurl

def notify_load_generator(env):
            
    ips = ''
    for ip in env.instance_ip_dict.itervalues():
        ips += str(ip) + ';'
                 
    url    = 'http://' + env.load_generator_ip + ':' + env.load_generator_port + '/update?ips=' + ips
    
    buf = cStringIO.StringIO()

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, buf.write)

    try:
        c.perform()
    except pycurl.error, error:
        errstr = error[1]
        print 'An error occurred: ' +  errstr
        
    buf.close()

def delete_vms(env, capacity_value):
        
    selected_vms    = select_vms_available_for_deletion(env, abs(int(capacity_value)))
        
    if len(selected_vms) > 0:
        
        print 'deleting server(s)'
        for i in range(0, len(selected_vms)):
                
            instance_id = str(selected_vms[i][0])
            
            delete_server(env, instance_id)
            delete_server_by_id(env, instance_id)
            
            del env.instance_ip_dict[instance_id]
    else:
        print 'no VMs available for deletion'
    
    return env.instance_ip_dict
            
class Actuator(t.Thread):
    
    def __init__(self, env, capacity):

        t.Thread.__init__(self)
        self.delay          = 5
        self.environment    = env
        self.capacity       = capacity
    
    def run(self):
        
        capacity_value  = self.capacity[1]         
    
        if capacity_value > 0:
            
            print 'creating server(s)'
            image_id        = self.environment.image_id
            flavor_id       = self.environment.flavor_id
            instance_name   = self.environment.instance_name
            
            instance_ids    = []
            
            for i in range(0, capacity_value):
                
                server_data = create_server(self.environment, image_id, flavor_id, instance_name)
                instance_id = server_data['server']['id']
                instance_ids.append(instance_id)
                
            instance_ips    = [] 
            
            if self.environment.enable_floating_ip: 
                
                time.sleep(10)
                
                instance_ip   = self.environment.floating_ip_list[0]
                del self.environment.floating_ip_list[0]
                add_floating_ip(self.environment, instance_id, instance_ip)
        
            else:    
                while len(instance_ids) > len(instance_ips):
                    
                    for instance_id in instance_ids:
                        instance_ip = get_server_ip_address(self.environment, str(instance_id))
                        
                        if not instance_ip == None:
                            
                            instance_ips.append(instance_ip)
                            self.environment.instance_ip_dict[str(instance_id)] = str(instance_ip)
                        
                    time.sleep(self.delay)
                
            notify_load_generator(self.environment)
            
        
        elif capacity_value < 0:

            print 'trying to delete server(s)'
            self.environment.instance_ip_dict   = delete_vms(self.environment, capacity_value)
            notify_load_generator(self.environment)
            
        
        
        