#!/bin/bash

if [ "$1" = "short" ]; then
	trace=(132)
else
	trace=(14)
fi

pred_interval=(5 10 20 30)

for (( i=0; i<${#trace[@]}; i++ ))
do
	echo "Trace: " ${trace[$i]}
	for (( j=0; j<${#pred_interval[@]}; j++ ))
	do
		echo "  Pred_Interval: " ${pred_interval[$j]}
		Rscript server-parallel-predictor.R ${trace[$i]} 16 LW $1 ${pred_interval[$j]}
		Rscript server-parallel-predictor.R ${trace[$i]} 16 LR $1 ${pred_interval[$j]}
		Rscript server-parallel-predictor.R ${trace[$i]} 16 AR $1 ${pred_interval[$j]}
		Rscript server-parallel-predictor.R ${trace[$i]} 16 ARIMA $1 ${pred_interval[$j]}
		Rscript server-parallel-predictor.R ${trace[$i]} 16 AC $1 ${pred_interval[$j]}
		Rscript server-parallel-predictor.R ${trace[$i]} 16 EN $1 ${pred_interval[$j]} &
	done
done
