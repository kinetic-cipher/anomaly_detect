
"""
anomaly_detect:

    Processes input CSV file of transactions and checks/flags tranactions which
    appear anomalous based on simple statistics.
    
"""
import sys
import csv
import argparse
import stats_accumulator as stats

#================= utility functions ==============

def get_cmd_line_args():
    """
       Get/retrieve the command-line arguments

       Inputs: 
           N/A
       Outputs:
           command-line argument as dictionary 
    """
    # create command line parser 
    parser = argparse.ArgumentParser()

    # setup positional (required) arguments
    parser.add_argument('input_file', action="store", 
                         help="input CSV file with format: AccountId, MerchantId, \
                               Transaction Amount") 

    parser.add_argument('log_file', action="store", 
                         help="output log file to write anomaly info") 

    # setup optional arguments
    parser.add_argument("-z", "--z_thresh", action="store", type=float, 
                        help="z-score threshold beyond which values are considered anomalous",
                        default=3)
    parser.add_argument("-n", "--num_samples_local", action="store", type=int, 
                        help="number of samples needed to switch from using global statistics \
                              for anomaly detection to local (Id-based) statistics", default=10)
    parser.add_argument("-v", "--verbose", 
                        action="store_true", help="enable verbose mode")

    # parse command line
    args = parser.parse_args()
    return args


def process_record(rec, customer_stats, merchant_stats, global_stats, z_thresh, 
                   num_samples_local, log_file):
    """
        Process the given record/transaction

        Inputs:
            rec: input record with fields AccountId, MerchantId, TransactionAmount
            customer_stats: StatsAccumulator instance used for collecting customer statistics
            merchant_stats: StatsAccumulator instance used for collecting merchant statistics
            global_stats: StatsAccumulator instance used for collecting global statistics
            z_thresh: z-score threshold beyond which values are considered anomalous  
            num_samples_local: number of samples needed to switch from using global statistics 
                               for anomaly detection to local (Id-based) statistics
            log_file: file object associated with the output log file 
        Outputs:  
            N/A
    """
    # validate number of fields
    if len(rec) != 3:
        print("WARNING [%s]: Unexpected record length ("+str(len(rec))+")" % 
               sys._getframe().f_code.co_name)
        print(rec)
        return

    # validate no empty/missing fields
    if not all( len(rec[k]) for k in range(len(rec))  ):  # all fields must be non-empty
        print("WARNING [%s]: record has missing fields" %
              sys._getframe().f_code.co_name)
        print(rec)
        return
 
    # validate transaction amount
    AccountId, MerchantId, Amount = rec
    try:
       Amount = float(Amount)
    except:
        print("WARNING [%s]: transaction amount non-numeric ("+Amount+")" 
              % sys._getframe().f_code.co_name)
        print(rec)
        return

    # update statistics
    GlobalId = 0
    customer_stats.update(AccountId, Amount)
    merchant_stats.update(MerchantId, Amount)
    global_stats.update(GlobalId,Amount)               
 
    # get global mean and stddev
    global_mean, global_stddev = global_stats.get_mean_stddev(GlobalId)

    # check for customer anomalies
    # if we have too few samples for this customer Id, fall back on global statistics
    # TODO: log local vs global mode used for decision?
    num_samples = customer_stats.get_num_samples(AccountId)
    if num_samples < num_samples_local:
       cur_mean, cur_stddev = global_mean, global_stddev
    else: 
       cur_mean, cur_stddev = customer_stats.get_mean_stddev(AccountId)

    if cur_stddev > 0:  # must be > 0, otherwise just comparing to mean
        if Amount > cur_mean + z_thresh*cur_stddev:
            log_file.write("ANOMALY (customer)(high): " + str(rec)[1:-1] + "\n")
        if Amount < cur_mean - z_thresh*cur_stddev:
            log_file.write("ANOMALY (customer)(low): " + str(rec)[1:-1] + "\n")

    # check for merchant anomalies 
    # if we have too few samples for this merchant Id, fall back on global statistics
    # TODO: log local vs global mode used for decision?
    num_samples = merchant_stats.get_num_samples(MerchantId)
    if num_samples < num_samples_local:
       cur_mean, cur_stddev = global_mean, global_stddev
    else: 
        cur_mean, cur_stddev = merchant_stats.get_mean_stddev(MerchantId)

    if cur_stddev > 0: # must be > 0, otherwise just comparing to mean
        if Amount > cur_mean + z_thresh*cur_stddev:
            log_file.write("ANOMALY (merchant)(high): " + str(rec)[1:-1] + "\n")
        if Amount < cur_mean - z_thresh*cur_stddev:
            log_file.write("ANOMALY (merchant)(low): " + str(rec)[1:-1] + "\n")


#================= main processing ==============

if __name__ == "__main__":

    print("processing...")

    # process the command line
    args = get_cmd_line_args()
    z_thresh = args.z_thresh
    num_samples_local = args.num_samples_local

    # create statistics accumulators
    customer_stats = stats.StatsAccumulator()
    merchant_stats = stats.StatsAccumulator()
    global_stats = stats.StatsAccumulator()

    # open input CSV file and process all rows after format fixes
    num_rec_processed = 0
    exclude_tokens=['X'] 
    with open(args.log_file,"w") as log_file:
        with open(args.input_file) as input_file:
            csv_reader = csv.reader(input_file, delimiter=',')
            for row in csv_reader:
                row_prep = list() 
                for token in row:
                   t = token.strip()
                   if t not in exclude_tokens:
                      row_prep.append(t)
            
                # process the row/record   
                process_record(row_prep, customer_stats, merchant_stats, global_stats, 
                               z_thresh, num_samples_local, log_file) 
                num_rec_processed +=1

                # verbose mode--print cumulative stats for all customer IDs
                if args.verbose:
                   for Id in customer_stats.stats_dict:
                       d = customer_stats.stats_dict[Id]
                       print("Account ID:%10s    mean:%8.2f    stddev:%6.2f    min:%2.2f    "
                             "max:%8.2f    num_samples:%6d" %( Id, d['mean'], 
                              d['stddev'], d['min'], d['max'], d['num_samples'] ))
                   print("="*100)     
 
    print("number of records processed:", num_rec_processed)


