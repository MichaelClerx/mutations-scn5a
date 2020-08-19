#!/usr/bin/env python
#
# Creates a csv file relating voltage shifts to amino acid index
#
from __future__ import print_function
import base
import numpy as np
def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        VoltageShiftIndices(),
        ]
class VoltageShiftIndices(base.Task):
    def __init__(self):
        super(VoltageShiftIndices, self).__init__('voltage_shift_indices')
        self._set_data_subdir('papergp')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            print('Loading voltage shift data')
            mutations = []
            for row in c.execute('select * from epdata'):
                idx = row['idx']
                dva = row['dva']
                dvi = row['dvi']
                dva = float(dva) if dva is not None else dva
                dvi = float(dvi) if dvi is not None else dvi
                mutations.append([idx, dva, dvi])
            filename = self.data_out('voltage-shift-indices.csv')
            print('Writing ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow([
                    'idx',
                    'dva',
                    'dvi',
                    ])
                for mutation in mutations:
                    w.writerow(mutation)
            print('Done')
if __name__ == '__main__':
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
