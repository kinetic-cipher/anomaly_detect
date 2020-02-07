# anomaly_detect

A very basic example of an anomaly detector using simple statistics. Input CSV data (records/transactions)
in the format (AccountId, MechantId, Amount) are processed and a z-score threshold is used to detect anomalies. 
Statistics are computed incrementally for memory efficiancy and to support online streaming applications.

