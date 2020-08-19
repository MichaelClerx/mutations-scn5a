#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
import base
import numpy as np
def tasks():
    return [
        TypesOfChangeAcids(),
        ]
class TypesOfChangeAcids(base.Task):
    """
    Counts the number of times each type of change (zero, late, act, inact)
    occurs in the various regions of SCN5A.
    
    """
    def __init__(self):
        super(TypesOfChangeAcids, self).__init__('types_of_change_acids')
        self._set_data_subdir('papergp')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            
            # Change selecting queries
            conditions = [
                'zero > 0',
                'act > 0',
                'inact > 0',
                'late > 0',
                ]

            # Acids
            acids = [str(r['key']) for r in c.execute(
                'select key from acid order by rowid')]
            
            # Number of changes per acid_from
            counts_fr = []
            for acid in acids:
                q = 'select count(idx) from ('
                q += ' select idx, sum(zero) as zero, sum(act) as act,'
                q += ' sum(inact) as inact, sum(late) as late'
                q += ' from epdata_annotated'
                q += ' where old = "' + acid + '"'
                counts = []
                for condition in conditions:
                    qc = q + ' and ' + condition + ' group by idx, new)'
                    counts.append(c.execute(qc).fetchone()[0])
                counts_fr.append(counts)
            # Write files            
            filename = self.data_out('acid-changes-1-from.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel', 'zero', 'act', 'inact', 'late'])
                for k, name in enumerate(acids):
                    w.writerow([k + 1, name] + counts_fr[k])
            relative_fr = np.array(counts_fr, dtype=float)
            relative_fr /= (np.sum(relative_fr, axis=1).reshape(20,1) + 1e-12)
            filename = self.data_out('acid-changes-relative-1-from.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel', 'zero', 'act', 'inact', 'late'])
                for k, name in enumerate(acids):
                    w.writerow([k + 1, name] + list(relative_fr[k]))
            
            # Number of changes per acid_to
            counts_to = []
            for acid in acids:
                q = 'select count(idx) from ('
                q += ' select idx, sum(zero) as zero, sum(act) as act,'
                q += ' sum(inact) as inact, sum(late) as late'
                q += ' from epdata_annotated'
                q += ' where new = "' + acid + '"'
                counts = []
                for condition in conditions:
                    qc = q + ' and ' + condition + ' group by idx, new)'
                    counts.append(c.execute(qc).fetchone()[0])
                counts_to.append(counts)
            # Write file            
            filename = self.data_out('acid-changes-2-to.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel', 'zero', 'act', 'inact', 'late'])
                for k, name in enumerate(acids):
                    w.writerow([k + 1, name] + counts_to[k])
            relative_to = np.array(counts_to, dtype=float)
            relative_to /= (np.sum(relative_to, axis=1).reshape(20,1) + 1e-12)
            filename = self.data_out('acid-changes-relative-2-to.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel', 'zero', 'act', 'inact', 'late'])
                for k, name in enumerate(acids):
                    w.writerow([k + 1, name] + list(relative_to[k]))

            # Write file combined data
            filename = self.data_out('acid-changes-3-combined.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel', 'zero', 'act', 'inact', 'late'])
                for k, name in enumerate(acids):
                    counts = []
                    for i in range(len(conditions)):
                        counts.append(counts_fr[k][i] + counts_to[k][i])
                    w.writerow([k + 1, name] + counts)
            relative_sum  = np.array(counts_to, dtype=float)
            relative_sum += np.array(counts_fr, dtype=float)
            relative_sum /= (np.sum(relative_sum, axis=1).reshape(20,1) +1e-12)
            filename = self.data_out('acid-changes-relative-3-combined.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow(['xaxis', 'xlabel', 'zero', 'act', 'inact', 'late'])
                for k, name in enumerate(acids):
                    w.writerow([k + 1, name] + list(relative_sum[k]))
            
if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
