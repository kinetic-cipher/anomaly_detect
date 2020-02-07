"""
 stats_test:

    Basic unit test of stats_accumulator to verify the incremental
    calculations of mean and std deviation agree with values computed
    via 'block' calculations using numpy.
"""

import numpy as np
import stats_accumulator as stats

Id = 0
stats_acc = stats.StatsAccumulator() 
X_test = np.random.randn(20)    # standard normal: mean=0, std = 1

print("\nX_test:", X_test)
print("\nmean(ref)  mean(acc)  stddev(ref)  stddev(acc)  ")
for k in range(len(X_test)):
    stats_acc.update(Id,X_test[k])    
    u_acc, std_acc = stats_acc.get_mean_stddev(Id)
    u_ref = np.mean( X_test[0:k+1] )     # k+1 to include k-th sample in test interval
    std_ref = np.std( X_test[0:k+1] )    # k+1 to include k-th sample in test interval
    print("%4.2f %4.2f %4.2f %4.2f" % (u_ref, u_acc, std_ref, std_acc) )

