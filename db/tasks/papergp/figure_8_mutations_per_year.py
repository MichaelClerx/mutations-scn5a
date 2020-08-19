#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
import base
import numpy as np
def tasks():
    return [
        MutationsPerYear(),
        ]
class MutationsPerYear(base.Task):
    """
    Counts mutations/epdata reported per year.
    """
    def __init__(self):
        super(MutationsPerYear, self).__init__('mutations_per_year')
        self._set_data_subdir('papergp')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            
            q = 'select year, count(old) as n from ('
            q += 'SELECT old, idx, new, pub, min(year) as year'
            q += ' FROM report inner join publication'
            q += ' on report.pub == publication.key'
            q += ' where pub != "exac" and year != 2016'
            q += ' group by idx, new)'
            q += ' group by year'
            filename = self.data_out('first-reports.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['year', 'first_reports'])
                for row in c.execute(q):
                    w.writerow([row['year'], row['n']])
                    
            q = 'select year, count(old) as n from ('
            q += 'SELECT old, idx, new, pub, year'
            q += ' FROM epdata inner join publication'
            q += ' on epdata.pub == publication.key'
            q += ' where year != 2016)'
            q += ' group by year'
            filename = self.data_out('epdata-reports.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['year', 'epdata_reports'])
                for row in c.execute(q):
                    w.writerow([row['year'], row['n']])

if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
