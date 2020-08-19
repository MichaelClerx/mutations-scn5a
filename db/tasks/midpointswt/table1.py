#!/usr/bin/env python3
#
# Generates the data for table 1: Number of measurements
#
import base
def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        Table1(),
        ]
class Table1(base.Task):
    def __init__(self):
        super(Table1, self).__init__('table1')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            
            totals = [0]*5
            def show(letter=None):
                q = 'select count(pub) from midpoints_wt'
                if letter:
                    q += ' where sequence = "' + letter + '"'
                else:
                    q += ' where sequence is null'
                n = next(c.execute(q))[0]
                totals[0] += n
                if letter:
                    print('Isoform ' + letter + ': ' + str(n))
                else:
                    print('Unknown : ' + str(n))
                n = next(c.execute(q + ' and beta1="yes"'))[0]
                totals[1] += n
                print('  with b1 : ' + str(n))
                n = next(c.execute(q + ' and cell="HEK"'))[0]
                totals[2] += n
                print('      HEK : ' + str(n))
                n = next(c.execute(q + ' and cell="Oocyte"'))[0]
                totals[3] += n
                print('   Oocyte : ' + str(n))
                n = next(c.execute(q + ' and cell="CHO"'))[0]
                totals[4] += n
                print('      CHO : ' + str(n))
                print('')
            
            show('a')
            show('b')
            show('astar')
            show('bstar')
            show(None)
            
            print('Totals: ' + str(totals))


if __name__ == '__main__':
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
