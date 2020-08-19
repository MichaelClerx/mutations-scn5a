#!/usr/bin/env python3
#
# Creates a csv file relating voltage shifts to conservedness
#
import base
import numpy as np
def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        VoltageShiftConservedness(),
        ]
class VoltageShiftConservedness(base.Task):
    def __init__(self):
        super(VoltageShiftConservedness, self).__init__(
            'voltage_shift_conservedness')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            # Load known shifts
            print('Loading voltage shift data')
            q = 'select * from epdata_filtered'
            q += ' where dva is not null and dvi is not null'
            mutations = []
            for row in c.execute(q):
                mutations.append([
                    int(row['idx']),
                    float(row['dva']),
                    float(row['dvi']),
                    ])
            # Load conservedness
            doms = {}
            hses = {}
            for row in c.execute('select * from conservedness'):
                doms[row['idx']] = row['dom']
                hses[row['idx']] = row['hse']
            # Store for graphing
            filename = self.data_out('voltage-shift-conservedness.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow([
                    'idx',
                    'dom',
                    'hse',
                    'dva',
                    'dvi',
                    'window',
                    ])
                for mutation in mutations:
                    idx, dva, dvi = mutation
                    dom = doms[idx]
                    hse = hses[idx]
                    window = dvi - dva
                    w.writerow([idx, dom, hse, dva, dvi, window])
            print('Done')
if __name__ == '__main__':
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
