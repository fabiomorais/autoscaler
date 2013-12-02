import threading as t
import time

from nova_util import create_server, delete_server
from actuator_helper import select_vms_avalable_for_deletion

def actuate_on_system(env, capacity):
            
    capacity_value  = capacity[0][1]         
    
    if(capacity_value > 0):
        
        image_id    = env.image_id
        flavor_id   = env.instance_id_list[0]
        instance_name =  'autoscaling'
        
        create_server(env, image_id, flavor_id, instance_name)

    else:
        delete_vms(env, capacity_value)

def delete_vms(env, capacity_value):
    
    selected_vms    = select_vms_avalable_for_deletion(env, abs(int(capacity_value)))
    
    print selected_vms
    
    if(len(selected_vms) > 0):
        for i in range(0, len(selected_vms)):
            delete_server(env, str(selected_vms[i][0]))
        
        