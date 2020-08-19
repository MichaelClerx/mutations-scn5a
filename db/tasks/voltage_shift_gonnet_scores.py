#!/usr/bin/env python3
#
# Creates a csv file relating voltage shifts to gonnet scores
#
import base
import numpy as np
import warnings
def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        VoltageShiftGonnetScores(),
        ]
class VoltageShiftGonnetScores(base.Task):
    """
    Calculates the gonnet scores for mutations with known epdata.
    """
    def __init__(self):
        super(VoltageShiftGonnetScores, self).__init__(
            'voltage_shift_gonnet_scores')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            # Load gonnet scores
            print('Loading gonnet scores')
            scores = {}
            for row in c.execute('select * from gonnet_score'):
                scores[row['key1'] + row['key2']] = row['score']
                scores[row['key2'] + row['key1']] = row['score']
            # Load voltage shifts
            print('Loading voltage shift data')
            q = 'select * from epdata_filtered'
            q += ' where dva is not null and dvi is not null'
            mutations = []
            for row in c.execute(q):
                mutations.append([
                    int(scores[row['old'] + row['new']]),
                    float(row['dva']),
                    float(row['dvi']),
                    ])
            # Create file relating the two
            filename = self.data_out('voltage-shift-gonnet-scores.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow([
                    'score',
                    'dva',
                    'dvi',
                    ])
                for mutation in mutations:
                    w.writerow(mutation)
            #
            # Divide the score axis into bins, for each bin, calculate
            #   (1/bin_size) * sum( dva )
            # and
            #   (1/bin_size) * sum( abs(dva) )
            # then repeat with dvi
            #
            print('Calculating binned sum of squares')
            # Create bins
            lo = -5.5
            hi = 5.5
            bw = 1
            centers = np.arange(lo, hi + bw, bw)
            lower = centers - bw * 0.5
            upper = centers + bw * 0.5
            # Gather shifts in bins
            dva = [[] for x in centers]
            dvi = [[] for x in centers]
            for mutation in mutations:
                score, da, di = mutation
                i = np.where((score >= lower) * (score < upper))[0][0]
                dva[i].append(da)
                dvi[i].append(di)
            # Calculate stats and write to file
            dva = [np.array(x) if x else np.array([0]) for x in dva]
            dvi = [np.array(x) if x else np.array([0]) for x in dvi]
            print([np.mean(x) for x in dva])
            print([np.mean(x) for x in dvi])
            filename = self.data_out('voltage-shift-gonnet-scores-binned.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow([
                    'center',
                    'dva-mean',
                    'dvi-mean',
                    'dva-std',
                    'dvi-std',
                    'dva-abs-mean',
                    'dvi-abs-mean',                    
                    ])
                data = [
                    centers,
                    [np.mean(x) for x in dva],
                    [np.mean(x) for x in dvi],
                    [np.std(x) for x in dva],
                    [np.std(x) for x in dvi],
                    [np.mean(np.abs(x)) for x in dva],
                    [np.mean(np.abs(x)) for x in dvi],
                    ]
                data = np.array([np.array(x) for x in data]).transpose()
                for row in data:
                    w.writerow(row)
            print('Done')
if __name__ == '__main__':
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
