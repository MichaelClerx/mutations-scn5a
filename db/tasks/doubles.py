#!/usr/bin/env python3
#
# Counts the number of positions, articles, positions with epdata etc.
#
import base
def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        Count(),
        ]
class Count(base.Task):
    def __init__(self):
        super(Count, self).__init__('count')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
           
            # Mutations with multiple epdata reports
            names = []
            parts = []
            counts = []
            q = 'select old, idx, new, n from ('
            q += 'select *, count(idx) as n from epdata group by idx, new'
            q += ') where n > 1 order by n desc, idx, new'
            for row in c.execute(q):
                names.append(row['old'] + str(row['idx']) + row['new'])
                parts.append((row['old'], row['idx'], row['new']))
                counts.append(row['n'])

            # Get data for mutations with multiple reports
            fields = ['act', 'inact', 'late', 'zero', 'sequence', 'cell',
                'beta1', 'pub']
            data = {}
            q = 'select * from epdata'
            q += ' where old=? and idx=? and new=?'
            for k, name in enumerate(names):
                d = {}
                for field in fields:
                    d[field] = []
                for row in c.execute(q, parts[k]):
                    for field in fields:
                        d[field].append(row[field])
                data[name] = d
            
            # Get list of mutations with inconsistencies
            ters = ['act', 'inact', 'late']
            bins = ['zero']
            issues = []
            for k, name in enumerate(names):
                d = data[name]
                for t in ters:
                    if -1 in d[t] and 1 in d[t]:
                        issues.append(name)
                        break
                else: # If didn't break
                    for b in bins:
                        if 0 in d[t] and 1 in d[t]:
                            issues.append(name)
                            break
            # Show output
            def pront(name):
                print(name)
                d = data[name]
                for k in range(len(d['act'])):
                    for f in fields:
                        print(d[f][k], end=' ')
                    print('')
            
            for name in names:
                if name not in issues:
                    pront(name)
            print()
            print('='*40)
            print('Mutations with doubles: ' + str(len(counts)))            
            print('Mutations with issues: ' + str(len(issues)))
            print('='*40)
            print()
            for name in issues:
                pront(name)
if __name__ == '__main__':
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
