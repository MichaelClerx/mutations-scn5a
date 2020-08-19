#!/usr/bin/env python3
import base
import numpy as np
def tasks():
    return [
        WindowedAverages(),
        ]
class WindowedAverages(base.Task):
    """
    Calculates the sliding window averages of mutations and scores
    """
    def __init__(self):
        super(WindowedAverages, self).__init__('windowed_averages')
        self._set_data_subdir('poster2014')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            # Get positions (may have gaps!)
            idx = []
            for r in c.execute('select idx from scn5a order by idx'):
                idx.append(r[0])
            idx = np.array(idx)
            # Get mutations for each position
            q = 'select distinct idx, new from report where pub != "exac"'
            mut = np.zeros(idx.shape)
            for r in c.execute(q):
                mut[r[0] - 1] = 1  # Positions start at 1
            # Get Human-squid-eel and domain alignment score
            hse = np.zeros(idx.shape, dtype=float)
            dom = np.zeros(idx.shape, dtype=float)
            q = 'select idx, hse, dom from conservedness order by idx'
            for k, r in enumerate(c.execute(q)):
                assert(r[0] == 1 + k) # Score should be stored for each idx
                hse[k] = r[1]
                dom[k] = r[2]
            #
            # 1. Sliding window averages for mutation count, hse score and dom
            #    score.
            #
            radius = 5
            ms = window(mut, radius)
            hs = window(hse, radius)
            ds = window(dom, radius)
            basename = 'windowed-averages'
            filename = self.data_out(basename + '.txt')
            print('Writing info to ' + filename)
            with open(filename, 'w') as f:
                f.write('Mutation count, human-squid-eel and domain-alignment'
                    ' score were measured per position, and then averaged'
                    ' using a sliding window with radius ' + str(radius)
                    + ' leading to a window size of ' + str(1 + 2 * radius)
                    + '. At the borders, where the window is smaller, the'
                    ' average is computed by dividing through the effective'
                    ' window size at that point.')
            filename = self.data_out(basename + '.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                c = self.csv_writer(f)
                c.writerow([
                    'position',
                    'mutation_count',
                    'hse_score',
                    'dom_score',
                    ])
                hs = iter(hs)
                ds = iter(ds)
                for k, m in enumerate(ms):
                    c.writerow([k+1, m, next(hs), next(ds)])
def window(x, r):
    """
    Returns the sliding window average of vector ``x``, performed with a
    window of radius ``r``.
    
    A radius ``r`` leads to a window size of ``w = 1 + 2 * r``.
    
    For a vector ``x=[1,2,3,4,5,6,7]`` with ``r=1``, ``y = window(x, w)``
    implies::
    
        y[0] = (       x[0] + x[1]) / 2 = 1.5
        y[1] = (x[0] + x[1] + x[2]) / 3 = 2.0
        y[2] = (x[1] + x[2] + x[3]) / 3 = 3.0 
        y[3] = (x[2] + x[3] + x[4]) / 3 = 4.0
        y[4] = (x[3] + x[4] + x[5]) / 3 = 5.0
        y[5] = (x[4] + x[5] + x[6]) / 3 = 6.0
        y[6] = (x[5] + x[6]       ) / 2 = 6.5
        
    """
    # Check radius
    r = int(r)
    if r < 1:
        raise ValueError('Window radius must be at least 1.')
    # Check input
    x = np.array(x, copy=False)
    if len(x.shape) > 1:
        raise ValueError('Array must be one dimensional.')
    # Array to create denominator
    y = np.ones(x.shape)
    # Create numerator/denominator arrays with padding
    n = len(x)
    m = n + 2 * r
    numer = np.zeros((m,), dtype=float)
    denom = np.zeros((m,), dtype=float)
    for i in range(1 + 2 * r):
        numer[i:min(i+n, m)] += x
        denom[i:min(i+n, m)] += y
    numer /= denom
    return numer[r:-r]
if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
