#!/usr/bin/env python3
#
# Calculates the mean and std of temperatures used in midpoint reports
#
import base
import numpy as np
import matplotlib.pyplot as pl
DEBUG = False
def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        MidpointTemperatures(),
        ]
class MidpointTemperatures(base.Task):
    def __init__(self):
        super(MidpointTemperatures, self).__init__('midpoint_temperatures')
        self._set_data_subdir('midpointswt')
    def gather(self, q):
        # Query db
        tmin, tmax, tmid = [], [], []
        with base.connect() as con:
            c = con.cursor()
            for row in c.execute(q):
                tmin.append(row['tmin'])
                tmax.append(row['tmax'])
                tmid.append(0.5 * (row['tmin'] + row['tmax']))
        # Create list of tmin, tmax, tmid
        tmin = np.array(tmin)
        tmax = np.array(tmax)
        tmid = np.array(tmid)
        print('TMid, mean: ' + str(np.mean(tmin)))
        print('TMid, std : ' + str(np.std(tmid)))
        print('2Sigma range: ' + str(4*np.std(tmid)))
        print('Min, max: ' + str(np.min(tmin)) + ', ' + str(np.max(tmax)))
        # Write file
        print('Done')
    def _run(self):
        # All data
        print('All data')
        q = 'select pub, tmin, tmax from midpoints_wt'
        q += ' where tmin != 0'
        q += ' AND tmax != 0'
        self.gather(q)
        # Largest subgroup
        print('Largest subgroup')
        q += ' and sequence == "astar"'
        q += ' and cell == "HEK"'
        q += ' and beta1 == "yes"'
        self.gather(q)
if __name__ == '__main__':
    #DEBUG = True
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
