suppressMessages(library(df2json, quietly=TRUE))

source("../src/predictor/general_predictor.R")

args  <- commandArgs(trailingOnly = TRUE)

if(length(args) > 0){

	method		     	<- as.character(args[1])
	history_json        <- as.character(args[2]) #in number of cores
	periodicity         <- as.numeric(args[3])
	prediction_horizon  <- as.numeric(args[4])
	pred_ahead	     	<- prediction_horizon / periodicity
	num_period			<- as.numeric(args[5])
	pred_json			<- as.character(args[6])
	pred_history_json	<- as.character(args[7])
	weight_json			<- as.character(args[8])
	
	pred_names          <- c("LW", "LR", "AC", "ARIMA", "AR")
	list_of_periods     <- list("LW"=0, "LR"=0, "AC"=0, "ARIMA"=0, "AR"=2016)
	
	df_json		     	<- json2df(history_json) # data.frame(cbind(timestamps, trace_util_cores),0, "Original")
	colnames(df_json)   <- c("TIMESTAMP", "CPU_UTIL_PERCENT", "CPU_UTIL", "CPU_ALLOC")
	
	
	df_trace            <- df_json[rev(rownames(df_json)), ]
	
	output_json			<- ""
	
	if(method == "LW"){
		estimated_trace     <- predict_LW(df_trace, periodicity, pred_ahead, num_period)
		output_json			<- df2json(estimated_trace)
	}else if(method == "AC"){
		estimated_trace     <- predict_AC(df_trace, periodicity, pred_ahead, num_period)
		output_json			<- df2json(estimated_trace)
	}else if(method == "LR"){
		estimated_trace     <- predict_LR(df_trace, periodicity, pred_ahead, num_period)
		output_json			<- df2json(estimated_trace)
	}else if(method == "AR"){
		estimated_trace     <- predict_AR(df_trace, periodicity, pred_ahead, num_period)
		output_json			<- df2json(estimated_trace)	
	}else if(method == "ARIMA"){
		estimated_trace     <- predict_ARIMA(df_trace, periodicity, pred_ahead, num_period)
		output_json			<- df2json(estimated_trace)
	}else if(method == "EN"){
	
		df_pred					<- json2df(pred_json) 
		df_pred	            	<- df_pred[rev(rownames(df_pred)), ]
		names(df_pred) 			<- c("TIMESTAMP", "CPU_UTIL", "PREDICTOR")
		
		df_pred_history			<- json2df(pred_history_json) 
		df_pred_history			<- df_pred_history[rev(rownames(df_pred_history)), ]
		names(df_pred_history)	<- c("TIMESTAMP", "CPU_UTIL", "PREDICTOR")
		
		df_weight				<- json2df(weight_json) 
		df_weight           	<- df_weight[rev(rownames(df_weight)), ]
		names(df_weight) 		<- c("TIMESTAMP", "WEIGHT", "PREDICTOR")
		
		result			     	<- predict_EN(df_trace, periodicity, pred_ahead, num_period, df_pred, df_pred_history, df_weight, pred_names, list_of_periods)
		
		estimated_json			<- df2json(result$estimated)
		weight_json				<- df2json(result$weight)
		
		output_json				<- paste(estimated_json, ";", weight_json, sep="")
	}
	
	cat(output_json)

}else{
	print("without args")
}