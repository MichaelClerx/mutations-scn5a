#!/usr/bin/env python3
#
# Calculates the mean of the standard deviation reported in the WT dataset.
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
        MidpointSigmas(),
        ]
class MidpointSigmas(base.Task):
    def __init__(self):
        super(MidpointSigmas, self).__init__('midpoint_sigmas')
        self._set_data_subdir('midpointswt')
    def gather(self, q, fname1, fname2):
        # Query db
        na, ni = [], []
        stda, stdi = [], []
        sema, semi = [], []
        with base.connect() as con:
            c = con.cursor()
            for row in c.execute(q):
                if row['na'] > 0:
                    na.append(row['na'])
                    stda.append(row['stda'])
                    sema.append(row['sema'])
                if row['ni'] > 0:
                    ni.append(row['ni'])
                    stdi.append(row['stdi'])
                    semi.append(row['semi'])
        # Calculate
        stda = np.array(stda)
        stdi = np.array(stdi)
        print('std a mean: ' + str(np.mean(stda)))
        print('std i mean: ' + str(np.mean(stdi)))
        print('2sr a mean: ' + str(4*np.mean(stda)))
        print('2sr i mean: ' + str(4*np.mean(stdi)))
        print('std a min: ' + str(np.min(stda)))
        print('std a max: ' + str(np.max(stda)))
        print('std i min: ' + str(np.min(stdi)))
        print('std i max: ' + str(np.max(stdi)))
        # Debug plot
        if False:
            pl.figure()
            pl.subplot(2,1,1)
            pl.plot(na, stda, 'o')
            pl.xlabel('na')
            pl.ylabel('stda')
            pl.subplot(2,1,2)
            pl.plot(ni, stdi, 'o')
            pl.xlabel('ni')
            pl.ylabel('stdi')
            pl.show()
        # Write files
        fname1 = self.data_out(fname1)
        print('Writing to ' + fname1)
        with open(fname1, 'w') as f:
            csv = self.csv_writer(f)
            csv.writerow(['na', 'stda'])
            data = []
            for k, n in enumerate(na):
                csv.writerow((n, stda[k]))
        fname2 = self.data_out(fname2)
        print('Writing to ' + fname2)
        with open(fname2, 'w') as f:
            csv = self.csv_writer(f)
            csv.writerow(['ni', 'stdi'])
            data = []
            for k, n in enumerate(ni):
                csv.writerow((n, stdi[k]))
        print('Done')
    def _run(self):
        # All data
        print('All data')
        fields = 'pub, na, ni, stda, stdi, sema, semi'
        q = 'select ' + fields + ' from midpoints_wt'
        self.gather(q, 'midpoints-na-stda.csv', 'midpoints-ni-stdi.csv')
        # Largest subgroup
        #print('Largest subgroup')
        #q += ' and key == "M77235"'
        #q += ' and celltype == "HEK"'
        #q += ' and beta1 == "yes"'
        #self.gather(q)
if __name__ == '__main__':
    #DEBUG = True
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()

