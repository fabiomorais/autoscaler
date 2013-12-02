from numpy.ma.core import ceil, maximum

def capacity_planning(environment, prediction, metric_type):
        
        predicted       = float(prediction[3])
        allocated       = float(prediction[4])
        
        if(metric_type == 'cpu_util'):
            
            capacity_list   = []
            
            for i in range(0, len(environment.instance_cpu_list)):

                instance_base   = float(environment.instance_cpu_list[i])
                capacity        = int(maximum(int(ceil((predicted / float(environment.reference_value) / instance_base))), int(environment.min_instance_num)).data) 
                variation       = capacity - allocated
                
                capacity_list.append((capacity, variation))
            
            return capacity_list