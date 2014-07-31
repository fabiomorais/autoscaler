from numpy.ma.core import ceil, maximum

def capacity_value(env, prediciton_value, cores_allocation_by_server):

        capacity    = int(maximum(int(ceil(round((prediciton_value / float(env.reference_value) / cores_allocation_by_server), 2))), int(env.min_instance_num)))
        return capacity 

def capacity_planning(environment, prediction, allocation):
        
        predicted                   = float(prediction[2])
        allocated_instances         = allocation[0]                                 #Total number of instances
        allocated_cores_by_sever    = allocation[1]                               #Total number of allocated coress
        
        print "prediction " + str(predicted)
        print "allocated instances " + str(allocated_instances)
        print "reference value " + str(environment.reference_value)
        
        capacity        = capacity_value(environment, predicted, allocated_cores_by_sever)
        variation       = capacity - allocated_instances
        
        print "capacity " + str(capacity)
              
        capacity_planning  =  (capacity, variation)
        
        print capacity_planning
        
        return capacity_planning
    