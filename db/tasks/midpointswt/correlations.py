#!/usr/bin/env python3
#
# Creates data for a graph of midpoint of activation and inactivation
# correlation, using only papers that reported both.
# Error bars are created based on the +/- 2*sigma range.
#
import base
import numpy as np
DEBUG = False
def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        MidpointCorrelations(),
        ]
class MidpointCorrelations(base.Task):
    def __init__(self):
        super(MidpointCorrelations, self).__init__('midpoint_correlations')
        self._set_data_subdir('midpointswt')
    def gather(self, q, fname1, fname2):
        # Query db
        data = []
        with base.connect() as con:
            c = con.cursor()
            for row in c.execute(q):
                data.append((
                    row['pub'],
                    row['va'],
                    #row['stda'],
                    2*row['stda'],
                    row['vi'],
                    #row['stdi'],
                    2*row['stdi'],
                    row['va'] - row['vi'],
                    ))
        # Write file
        fname1 = self.data_out(fname1)
        print('Writing to ' + fname1)
        with open(fname1, 'w') as f:
            csv = self.csv_writer(f)
            csv.writerow(['pub', 'va', '+-', 'vi', '+-', 'dv'])
            for row in data:
                csv.writerow(row)
        print('Collected data from ' + str(len(data)) + ' reports.')
        #
        # Correct with linear regression
        #
        print('Subtracting linear regression...')
        # Gather data
        va = []
        vi = []
        for row in data:
            va.append(row[1])
            vi.append(row[3])
        va = np.array(va)
        vi = np.array(vi)
        # Fit line
        b, a = np.polyfit(va, vi, 1)
        if DEBUG:
            import matplotlib.pyplot as pl
            pl.figure()
            pl.plot(va, vi, 'o')
            x = np.linspace(np.min(va)-10, np.max(va)+10, 1000)
            y = a + b * x
            pl.plot(x, y)
        # Subtract
        if DEBUG:
            pl.figure()
            pl.plot(va, vi - (a + b * va), 'o')
            pl.show()
        print('Coefficients: ' + str(a) + ', ' + str(b))
        # Write file
        fname2 = self.data_out(fname2)
        print('Writing to ' + fname2)
        with open(fname2, 'w') as f:
            csv = self.csv_writer(f)
            csv.writerow(['pub', 'va', '+-', 'vic', '+-'])
            for k, row in enumerate(data):
                row = list(row[:-1])
                row[3] = row[3] - (a + b * row[1])
                csv.writerow(row)
        # Get Pearson correlation coefficient
        print('Pearson correlation coefficient: '
             + str(np.corrcoef(va, vi)[1,0]))
        print('Done')
    def _run(self):
        # All data
        q = 'select pub, va, stda, vi, stdi from midpoints_wt'
        q += ' where va != 0'
        q += ' AND vi != 0'
        q += ' AND stda != 0'
        q += ' AND stdi != 0'
        fname1 = 'midpoint-correlations.csv'
        fname2 = 'midpoint-correlations-regression.csv'
        self.gather(q, fname1, fname2)
        # Largest subgroup
        q += ' and sequence == "astar"'
        q += ' and cell == "HEK"'
        q += ' and beta1 == "yes"'
        fname1 = 'midpoint-correlations-largest-subgroup.csv'
        fname2 = 'midpoint-correlations-regression-largest-subgroup.csv'
        self.gather(q, fname1, fname2)
if __name__ == '__main__':
    #DEBUG = True
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
