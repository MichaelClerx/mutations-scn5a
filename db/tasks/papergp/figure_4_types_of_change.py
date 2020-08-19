#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
import base
import numpy as np
def tasks():
    return [
        TypesOfChange(),
        ]
class TypesOfChange(base.Task):
    """
    Counts the number of times each type of change (zero, late, act, inact)
    occurs in the various regions of SCN5A.

    """
    def __init__(self):
        super(TypesOfChange, self).__init__('types_of_change')
        self._set_data_subdir('papergp')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()

            # Change selecting queries
            condition_names = [
                'zero', 'act', 'inact', 'late', 'changed', 'unchanged',
            ]
            conditions = [
                'zero > 0',
                'act > 0',
                'inact > 0',
                'late > 0',
                # Changed / no change reported:
                '(zero > 0 or act > 0 or inact > 0 or late > 0)',
                '(zero < 1 and act < 1 and inact < 1 and late < 1)',
            ]

            #
            # Number of changes per domain
            #

            # Domain names
            domain_names = [
                r['name'] for r in c.execute('select name from domain')]

            # Count number of each type of change per domain
            # Note that epdata_annotated contains each unique mutation only
            # once (although its fields such as `act` show a sum of votes for
            # whether or not it was affected, based on all available reports).
            domain_counts = []
            for name in domain_names:
                q = 'select count(idx) from epdata_annotated'
                q += ' where domain = "' + name + '"'
                counts = []
                for condition in conditions:
                    qc = q + ' and ' + condition
                    counts.append(c.execute(qc).fetchone()[0])
                domain_counts.append(counts)

            # Write files
            filename = self.data_out('changes-1-per-domain.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel'] + condition_names)
                for k, name in enumerate(domain_names):
                    w.writerow([k + 1, name] + domain_counts[k])

            filename = self.data_out('changes-relative-1-per-domain.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel'] + condition_names)
                for k, name in enumerate(domain_names):
                    r = np.array(domain_counts[k])
                    s = np.sum(r) or 1
                    w.writerow([k + 1, name] + list(r / s))

            #
            # Number of changes per region type
            #

            # Region type names
            regtype_names = [
                r['name'] for r in c.execute('select name from regtype')]

            # Count number of each type of change per regtype
            regtype_counts = []
            for name in regtype_names:
                q = 'select count(idx) from epdata_annotated'
                q += ' where regtype = "' + name + '"'
                counts = []
                for condition in conditions:
                    qc = q + ' and ' + condition
                    counts.append(c.execute(qc).fetchone()[0])
                regtype_counts.append(counts)

            # Write files
            filename = self.data_out('changes-2-per-regtype.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel'] + condition_names)
                for k, name in enumerate(regtype_names):
                    w.writerow([k + 1, name] + regtype_counts[k])

            filename = self.data_out('changes-relative-2-per-regtype.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel'] + condition_names)
                for k, name in enumerate(regtype_names):
                    r = np.array(regtype_counts[k])
                    s = np.sum(r) or 1
                    w.writerow([k + 1, name] + list(r / s))

            #
            # Number of changes per region
            #

            # Region names
            q = 'select name from region order by start'
            region_names = [r['name'] for r in c.execute(q)]

            # Number of mutations per region
            region_counts = []
            for name in region_names:
                q = 'select count(idx) from epdata_annotated'
                q += ' where region = "' + name + '"'
                counts = []
                for condition in conditions:
                    qc = q + ' and ' + condition
                    counts.append(c.execute(qc).fetchone()[0])
                region_counts.append(counts)

            # Write files
            filename = self.data_out('changes-3-per-region.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel'] + condition_names)
                for k, name in enumerate(region_names):
                    w.writerow([k + 1, name] + region_counts[k])

            filename = self.data_out('changes-relative-3-per-region.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel'] + condition_names)
                for k, name in enumerate(region_names):
                    r = np.array(region_counts[k])
                    s = np.sum(r) or 1
                    w.writerow([k + 1, name] + list(r / s))


if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
