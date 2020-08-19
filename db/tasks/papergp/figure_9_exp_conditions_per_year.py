#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
import base
import numpy as np
def tasks():
    return [
        ExpConditionsPerYear(),
        ]
class ExpConditionsPerYear(base.Task):
    """
    Collects data about experimental conditions per year.
    """
    def __init__(self):
        super(ExpConditionsPerYear, self).__init__('exp_conditions_per_year')
        self._set_data_subdir('papergp')
    def make(self, alpha):
        """
        Alpha=True, make file for alpha subunits
        Alpha=False, make file for beta subunits
        """
        with base.connect() as con:
            c = con.cursor()
            
            # Get years to find data for
            q = 'select min(year)'
            q += ' from epdata inner join publication'
            q += ' on epdata.pub = publication.key'
            year1 = next(c.execute(q))[0]
            years = range(year1, 2016)

            # Gather data
            data = {}            
            if alpha:
                # Alpha subunits
                names = []
                q = 'select distinct sequence from epdata'
                for row in c.execute(q):
                    names.append(row['sequence'])
                names.remove(None)
                q = 'select year, count(old) as n'
                q += ' from epdata inner join publication'
                q += ' on epdata.pub = publication.key'
                q += ' where sequence = ? and year < 2016'
                q += ' group by year'
                for name in names:
                    ydata = [0]*len(years)
                    for row in c.execute(q, (name,)):
                        ydata[row['year'] - year1] = row['n']
                    data[name] = ydata
                q = 'select year, count(old) as n'
                q += ' from epdata inner join publication'
                q += ' on epdata.pub = publication.key'
                q += ' where sequence is null and year < 2016'
                q += ' group by year'
                ydata = [0]*len(years)
                for row in c.execute(q):
                    ydata[row['year'] - year1] = row['n']
                data['Unknown'] = ydata
                names.append('Unknown')
                
                # Tweak order
                tweak = [
                    'achen',
                    'bstar',
                    'astar',
                    'b',
                    'a',
                    'Unknown',                    
                    ]
                if set(names) != set(tweak):
                    raise Exception('Tried to tweak order of lines, but custom'
                        ' order is lacking some values! Should have: '
                        + ','.join(names))
                names = tweak
            else:
                # Beta subunits
                names = ['yes', 'no']
                q = 'select year, count(old) as n'
                q += ' from epdata inner join publication'
                q += ' on epdata.pub = publication.key'
                q += ' where beta1 = ? and year < 2016'
                q += ' group by year'
                for name in names:
                    ydata = [0]*len(years)
                    for row in c.execute(q, (name,)):
                        ydata[row['year'] - year1] = row['n']
                    data[name] = ydata
            
            # Filenames
            if alpha:
                basename = 'alpha_per_year'
            else:
                basename = 'beta1_per_year'
            
            # Write output
            iters = []
            iters.append(iter(years))
            year_rows = []
            for name in names:
                iters.append(iter(data[name]))
            filename = self.data_out(basename + '.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['year'] + names)
                for k, year in enumerate(years):
                    row = [next(i) for i in iters]
                    w.writerow(row)
                    year_rows.append(np.array(row[1:]))

            # Plot same data but as fraction
            for k, row in enumerate(year_rows):
                if np.sum(row) > 0:
                    year_rows[k] = row / np.sum(row)
            filename = self.data_out(basename + '_frac.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['year'] + names)
                for k, year in enumerate(years):
                    w.writerow([year] + list(year_rows[k] * 100))

            # Plot same data but as cumulative fractions
            for k, row in enumerate(year_rows):
                offset = 0
                for i, x in enumerate(row):
                    year_rows[k][i] += offset
                    offset += x
            filename = self.data_out(basename + '_cumfrac.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['year'] + names)
                for k, year in enumerate(years):
                    w.writerow([year] + list(year_rows[k]))
            
    def _run(self):
        self.make(alpha=True)
        self.make(alpha=False)

if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
