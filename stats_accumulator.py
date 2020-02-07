"""
stats_accumulator:
    Statistics Accumulator. Used to collect simple statistics incrementally for "online" streaming applications.
    Incremental calculations are also formulated to be numerically stable, avoiding large sums and sums-of-squares.
    Multiple entities can be tracked through the use of a unique Id.

    references for incremental calculations:
        https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
        http://datagenetics.com/blog/november22017/index.html  
"""
import sys
import math

class StatsAccumulator:

    def __init__(self):
        """
            Initializer       
        """
        self.reset()

    def _update_min(self,Id,val):
        """
           Internal method for updating cumulative minimum. This
           method should not be called directly.

           Inputs:
              Id: unique identifier for entity being tracked
              val: value to accumulate into tracked statistics
           Outputs:
              N/A
        """
        if Id in self.stats_dict:
           prev_min = self.stats_dict[Id]['min']
           new_min = min( val, prev_min) 
           self.stats_dict[Id]['min'] = new_min
        else:
            print("WARNING [%s]: Unknown ID ("+str(Id)+")" % 
                  sys._getframe().f_code.co_name)

    def _update_max(self,Id,val):
        """
           Internal method for updating cumulative maximum. This
           method should not be called directly.

           Inputs:
              Id: unique identifier for entity being tracked
              val: value to accumulate into tracked statistics
           Outputs:
              N/A
        """
        if Id in self.stats_dict:
           prev_max = self.stats_dict[Id]['max']
           new_max = max( val, prev_max) 
           self.stats_dict[Id]['max'] = new_max
        else:
            print("WARNING [%s]: Unknown ID ("+str(Id)+")" % 
                  sys._getframe().f_code.co_name)

    def _update_mean_stddev(self,Id,val):
        """
           Internal method for updating cumulative mean and standard deviation. 
           This method should not be called directly.

           Inputs:
              Id: unique identifier for entity being tracked
              val: value to accumulate into tracked statistics
           Outputs:
              N/A
        """
        if Id in self.stats_dict:
           prev_mean = self.stats_dict[Id]['mean']
           prev_sum_sq_diff = self.stats_dict[Id]['sum_sq_diff']
           num_samples = self.stats_dict[Id]['num_samples'] + 1
           new_mean = prev_mean + (val-prev_mean)/num_samples
           new_sum_sq_diff = prev_sum_sq_diff + (val-prev_mean)*(val-new_mean)
           new_stddev = math.sqrt( max(0,new_sum_sq_diff/num_samples) )
           self.stats_dict[Id]['mean'] = new_mean
           self.stats_dict[Id]['sum_sq_diff'] = new_sum_sq_diff
           self.stats_dict[Id]['stddev'] = new_stddev
           self.stats_dict[Id]['num_samples'] = num_samples
        else:
            print("WARNING [%s]: Unknown ID ("+str(Id)+")" % 
                  sys._getframe().f_code.co_name)
       

    def get_mean_stddev(self,Id):
        """
           Gets/retrieves the current cumulative mean and standard deviation
           associated with the given Id.

           Inputs:
              Id: unique identifier for entity being tracked
           Outputs:
              mean, std_deviation
        """
        return self.stats_dict[Id]['mean'], self.stats_dict[Id]['stddev']
    

    def get_num_samples(self,Id):
        """
           Gets/retrieves the number of samples associated with the given Id
           which have been processed.

           Inputs:
              Id: unique identifier for entity being tracked
           Outputs:
              num_samples
        """
        return self.stats_dict[Id]['num_samples']


    def update(self, Id, val):
        """
           Updates the accumulated statistics given a new input value.

           Inputs:
              Id: unique identifier for entity being tracked
              val: value to accumulate into tracked statistics
           Outputs:
              N/A
        """
        if Id not in self.stats_dict:
            self.stats_dict[Id] = dict()
            self.stats_dict[Id]['mean'] = 0
            self.stats_dict[Id]['stddev'] = 0
            self.stats_dict[Id]['sum_sq_diff'] = 0  # used with stddev
            self.stats_dict[Id]['min'] = 0
            self.stats_dict[Id]['max'] = 0
            self.stats_dict[Id]['num_samples'] = 0
       
        self._update_mean_stddev(Id,val)                      
        self._update_min(Id,val)                      
        self._update_max(Id,val)
                      

    def reset(self):
        """
           Resets to initialized state

           Inputs:
              N/A
           Outputs:
              N/A
        """
        self.stats_dict = dict()
        

