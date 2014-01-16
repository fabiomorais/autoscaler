suppressMessages(library(foreach, quietly=TRUE))
suppressMessages(library(plyr, quietly=TRUE))
suppressMessages(library(signal, quietly=TRUE))
suppressMessages(library(forecast, quietly=TRUE))

predict_AR = function(df_trace, periodicity, pred_ahead, num_period){
    
	# Horizon
    future_start_time	<- periodicity
    future_end_time		<- periodicity * pred_ahead
    
	workload_end_time         <- df_trace[,"TIMESTAMP"][nrow(df_trace)]
    
    future_win_start_time	<- as.numeric(workload_end_time + future_start_time)
    future_win_end_time		<- as.numeric(workload_end_time + future_end_time)
    
    # Timestamps to predict
    fut_timestamp		<- seq(future_win_start_time, future_win_end_time, periodicity)
    fut_timestamp		<- fut_timestamp[pred_ahead]
        
	ts_util_core		<- ts(df_trace$CPU_UTIL)
        
	order_max		<- max(1, min(num_period, length(ts_util_core)-1))
        
	# AR Algorithm
	ar_util_core		<- ar(ts_util_core, aic = T, order.max = order_max)
        
	# Final prediction
	util_core_prediction	<- predict(ar_util_core, n.ahead=pred_ahead)$pred[pred_ahead]
    util_core_prediction	<- max(0, util_core_prediction)
    
	prediction_result	<- data.frame(TIMESTAMP=fut_timestamp, CPU_UTIL=util_core_prediction)
        
    prediction_result
}

predict_AC = function(df_trace, periodicity, pred_ahead, num_period){
    
    # Horizon
    future_start_time	<- periodicity
    future_end_time		<- periodicity * pred_ahead
        
    # ACF algorithm
    acf_result		<- acf(df_trace$CPU_UTIL, lag.max = length(df_trace$CPU_UTIL)/2, plot=FALSE)
        
    acf_pos			<- (acf_result$acf > 0)
    j				<- 2
        
    while(acf_pos[j] && j <= length(acf_pos)){
    	j <- j+1
    }
        
    #Verificar se sao duas fases de auto-correlacao forte
    if(j > length(acf_pos)) {
    	init <- 2   
   	}else{
        init <- j
    }
        
    acf_value <- acf_result$acf[init:length(acf_result$acf)]
        
    max_acf = -1
    max_acf_index = -1
    
    for(i in 1:length(acf_value)){
    	tmp_acf = sum(acf_value[i:(i+pred_ahead-2)], na.rm = T)
        if (tmp_acf > max_acf){
        	max_acf = tmp_acf
            max_acf_index = i
        }
    }
        
    acf_index <- (max_acf_index:(max_acf_index + pred_ahead - 2)) + init - 1
    
    window_trace		     <- df_trace[acf_index,]
    
    workload_end_time         <- df_trace[,"TIMESTAMP"][nrow(df_trace)]
    
    future_win_start_time	<- as.numeric(workload_end_time + future_start_time)
    future_win_end_time		<- as.numeric(workload_end_time + future_end_time)
    
    # Timestamps to predict
    fut_timestamp		<- seq(future_win_start_time, future_win_end_time, periodicity)
    fut_timestamp		<- fut_timestamp[pred_ahead]
        
    prediction_result	<- data.frame(TIMESTAMP=fut_timestamp, CPU_UTIL=window_trace[,"CPU_UTIL"])
        
    prediction_result
}

predict_ARIMA = function(df_trace, periodicity, pred_ahead, num_period){
    
	# Horizon
    future_start_time	<- periodicity
    future_end_time		<- periodicity * pred_ahead
    
	workload_end_time         <- df_trace[,"TIMESTAMP"][nrow(df_trace)]
    
    future_win_start_time	<- as.numeric(workload_end_time + future_start_time)
    future_win_end_time		<- as.numeric(workload_end_time + future_end_time)
    
    # Timestamps to predict
    fut_timestamp		<- seq(future_win_start_time, future_win_end_time, periodicity)
    fut_timestamp		<- fut_timestamp[pred_ahead]
    
	# ARIMA algorithm
	ts_util_core		<- ts(df_trace$CPU_UTIL)
        
	order_max			<- max(1, min(num_period, length(ts_util_core)-1))
        
	arima_util_core		<- auto.arima(ts_util_core, stationary=TRUE, stepwise=FALSE, ic="aic", max.p=num_period, trace=FALSE, xreg=seq(1,length(ts_util_core)))
        
	# Final prediction
	util_core_prediction	<- predict(arima_util_core, n.ahead=pred_ahead, newxreg=seq(1,length(ts_util_core)))$pred[pred_ahead]
    util_core_prediction	<- max(0, util_core_prediction)
        
	prediction_result	<- data.frame(TIMESTAMP=fut_timestamp, CPU_UTIL=util_core_prediction)
        
    prediction_result
}

predict_LR = function(df_trace, periodicity, pred_ahead, num_period){
    
	# Horizon
    future_start_time	<- periodicity
    future_end_time		<- periodicity * pred_ahead
    
    slot_number		<- nrow(df_trace)
    
	# ACF based algorithm
	acf_result		<- acf(df_trace$CPU_UTIL, lag.max = length(df_trace$CPU_UTIL)/2, plot=FALSE)
        
	df_acf			<- (acf_result$acf > 0.3)
        
	last_slot <- 2
	while(df_acf[last_slot] && (last_slot <= slot_number)){
		last_slot 	<- last_slot + 1
	}
        
	lag_number	<- max(1, last_slot)
        
	init_slot	<- max(1,(slot_number - lag_number))
	end_slot	<- slot_number
        
	slots_trace	<- seq(init_slot, end_slot)
        
	regression	<- lm(df_trace$CPU_UTIL[slots_trace] ~ slots_trace)
        
	new_slot_trace	<- seq(slot_number + 1, slot_number + pred_ahead)	
        
	# Final prediction
	util_core_prediction	<- predict(regression, data.frame(slots_trace = new_slot_trace))[pred_ahead]
	util_core_prediction	<- max(0, util_core_prediction)
 
    workload_end_time        <- df_trace[,"TIMESTAMP"][nrow(df_trace)]
        
    future_win_start_time    <- as.numeric(workload_end_time + future_start_time)
	future_win_end_time		 <- as.numeric(workload_end_time + future_end_time)
        
    # Timestamps to predict
	fut_timestamp		<- seq(future_win_start_time, future_win_end_time, periodicity)
	fut_timestamp		<- fut_timestamp[2]
        
	prediction_result	<- data.frame(TIMESTAMP=fut_timestamp, CPU_UTIL=util_core_prediction)
	prediction_result
        
}


predict_LW = function(df_trace, periodicity, pred_ahead, num_period){
    
	# Horizon
    future_start_time	<- periodicity
    future_end_time		<- periodicity * pred_ahead
        
    # Trace beggining
    workload_start_time	<- df_trace[,"TIMESTAMP"][1]
        
    future_win_start_time	<- as.numeric(workload_start_time + future_start_time)
    future_win_end_time		<- as.numeric(workload_start_time + future_end_time)
        
    # Timestamps to predict
    fut_timestamp		<- seq(future_win_start_time, future_win_end_time, periodicity)
    fut_timestamp		<- fut_timestamp[2]
        
    # The result is the previous CPU_UTIL in the window, only.
    window_trace        	<- subset(df_trace, TIMESTAMP == workload_start_time)
    prediction_result		<- data.frame(TIMESTAMP=fut_timestamp, CPU_UTIL=window_trace[,"CPU_UTIL"])
        
    prediction_result
}

predict_EN = function(df_trace, periodicity, pred_ahead, num_period, df_pred, df_pred_history, df_weight, pred_names, list_of_periods){
   	
    df_pred$PREDICTOR    <- as.character(df_pred$PREDICTOR)
    df_pred		         <- subset(df_pred, !(as.character(PREDICTOR) == "EN"))
   
    list_of_df_pred	     <- dlply(df_pred, .(PREDICTOR))
    list_of_df_pred	     <- lapply(list_of_df_pred, function(x) { x$CPU_UTIL <- pmax(x$CPU_UTIL, 0); x})

    timestamp_pred 	     <- list_of_df_pred[[1]][1,1]
    
    weight     <- c()
    
    calc_cost <- function(prediction, raw_data){
    
    	 if(length(raw_data) == 0){
		  
		  		print("error")
		  		print(df_trace)
		  		print(df_pred)
		  		print(df_pred_history)
		 }
		 
		T_hit <- 5
		T_miss <- 1040
		R_vm <- 400
		BETA <- 0.5
		
		cost <- if(raw_data < prediction) {
			(BETA * raw_data * T_hit) + ((1-BETA)*(prediction - raw_data) * R_vm)
		}else{
			(BETA * prediction * T_hit) + ((raw_data-prediction) * T_miss)
		}
		cost
	}
    
    if((length(df_weight) > 0) && (nrow(df_weight) > 0) && (length(df_pred_history) > 0) && (length(df_trace) > 0)){    
    
          df_weight                    <- df_weight[with(df_weight, order(PREDICTOR)), ] 
          
          df_pred_history$PREDICTOR    <- as.character(df_pred_history$PREDICTOR)
          df_pred_history     	    <- subset(df_pred_history, !(as.character(PREDICTOR) == "EN"))
          
          list_of_df_pred_his <- dlply(df_pred_history, .(PREDICTOR))
          list_of_df_pred_his	<- lapply(list_of_df_pred_his, function(x) { x$CPU_UTIL <- pmax(x$CPU_UTIL, 0); x})
    
          timestamp_pred_his  <- list_of_df_pred_his[[1]][1,1]

          weight			<- data.frame(rep(timestamp_pred_his, length(pred_names)), df_weight$WEIGHT, pred_names)
          names(weight)       <- c("TIMESTAMP", "WEIGHT", "PREDICTOR")

          #cost 			<- as.matrix(sapply(list_of_df_pred_his, function(x) calc_cost(x[1,2], subset(df_trace, (TIMESTAMP %/% 100) == (timestamp_pred_his %/% 100))$CPU_UTIL), simplify=TRUE))
          cost 			<- as.matrix(sapply(list_of_df_pred_his, function(x) calc_cost(x[1,2], df_trace$CPU_UTIL[1]), simplify=TRUE))
          error 		     <- ((sum(cost)/cost) * as.vector(weight[1:nrow(weight), 2]))
          
          weight 		     <- data.frame(rep(timestamp_pred, length(pred_names)), error/sum(error), sort(pred_names))
          names(weight)       <- c("TIMESTAMP", "WEIGHT", "PREDICTOR")
          rownames(weight)    <- seq(1, nrow(weight))

     }else{
    	     
          weight 		     <- data.frame(rep(timestamp_pred, length(pred_names)), rep(1/length(pred_names), length(pred_names)), sort(pred_names))
          names(weight) 	     <- c("TIMESTAMP", "WEIGHT", "PREDICTOR")
    }
    
    weight                    <- weight[with(weight, order(PREDICTOR)), ] 
    
    ensemble_pred 		     <- sum(weight[1:nrow(weight),2] * sapply(list_of_df_pred, function(x) max(0, x[1,2])))
    prediction_result	     <- data.frame(timestamp_pred, ensemble_pred)
    names(prediction_result)  <- c("TIMESTAMP","CPU_UTIL")
    
    list(estimated = prediction_result, weight = weight)
}