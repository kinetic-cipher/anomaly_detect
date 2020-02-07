
# run anomaly detect with z-score threshold of 3 and local sample number threshold of 10 in VERBOSE mode
# In this mode, the accumulated local statistics for all AccountIds (customers) are printed out at each transaction 
python anomaly_detect.py -v -z 3 -n 10 task2_data_small.csv output.log


