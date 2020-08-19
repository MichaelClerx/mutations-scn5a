#!/usr/bin/env python
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

            # Count positions
            n = next(c.execute('select count(idx) from scn5a;'))[0]
            print('Positions: ' + str(n))
            # Count articles
            n = next(c.execute('select count(key) from publication;'))[0]
            print('Articles: ' + str(n))
            # Count journals
            n = next(c.execute('select count(key) from journal;'))[0]
            print('Journals: ' + str(n))

            # Count mutations
            # Note: `mutation` lists only unique (old, idx, new) pairs, not
            # reports of mutations!
            n = next(c.execute('select count(old) from mutation;'))[0]
            print('Mutations               : ' + str(n))
            # Count unique mutation positions
            q = 'select count(idx) from '\
                '(select distinct idx from mutation);'
            n = next(c.execute(q))[0]
            print('Positions with mutations: ' + str(n))

            # Count mutations (no exac)
            q = 'select count(idx) from '\
                '(select distinct idx, new from report where pub != "exac");'
            n = next(c.execute(q))[0]
            print('Mutations (no exac)               : ' + str(n))
            # Count unique mutation positions (no exac)
            q = 'select count(distinct idx) from report where pub != "exac"'
            n = next(c.execute(q))[0]
            print('Positions with mutations (no exac): ' + str(n))

            # EP Data measurements
            n = next(c.execute('select count(idx) from epdata;'))[0]
            print('EP measurements: ' + str(n))

            # Mutations with measured EP
            q = 'select count(idx) from epdata_outcomes'
            n = next(c.execute(q))[0]
            print('Mutations with epdata: ' + str(n))
            # Positions with measured EP
            q = 'select count(distinct idx) from epdata_outcomes'
            n = next(c.execute(q))[0]
            print('Positions with epdata: ' + str(n))

            # Mutations with any change to EP
            q = 'select count(idx) from epdata_outcomes'
            q += ' where zero>0 or act>0 or inact>0 or late>0'
            n = next(c.execute(q))[0]
            print('Mutations with change to epdata: ' + str(n))
            q = 'select count(distinct idx) from epdata_outcomes'
            q += ' where zero>0 or act>0 or inact>0 or late>0'
            n = next(c.execute(q))[0]
            print('Positions with change to epdata: ' + str(n))
            q = 'select distinct idx from epdata_outcomes'
            q += ' where zero>0 or act>0 or inact>0 or late>0'
            # Mutations without any change to EP
            q = 'select count(idx) from epdata_outcomes'
            q += ' where zero<1 and act<1 and inact<1 and late<1'
            n = next(c.execute(q))[0]
            print('Mutations with no change to epdata: ' + str(n))
            q = 'select count(distinct idx) from epdata_outcomes'
            q += ' where zero<1 and act<1 and inact<1 and late<1'
            n = next(c.execute(q))[0]
            print('Positions with no change to epdata: ' + str(n))

            # Mutations causing zero current
            q = 'select count(idx) from ' \
                '(select distinct idx, new from epdata_outcomes where zero>0);'
            n = next(c.execute(q))[0]
            print('Mutations with zero=1: ' + str(n))
            # Positions causing zero current
            q = 'select count(idx) from ' \
                '(select distinct idx from epdata_outcomes where zero>0);'
            n = next(c.execute(q))[0]
            print('Positions with zero=1: ' + str(n))

            # Mutations affecting activation
            q = 'select count(idx) from ' \
                '(select distinct idx, new from epdata_outcomes where act>0);'
            n = next(c.execute(q))[0]
            print('Mutations with act=1: ' + str(n))
            # Positions affecting activation
            q = 'select count(idx) from ' \
                '(select distinct idx from epdata_outcomes where act>0);'
            n = next(c.execute(q))[0]
            print('Positions with act=1: ' + str(n))

            # Mutations affecting inactivation
            q = 'select count(idx) from ' \
                '(select distinct idx, new from epdata_outcomes where inact>0);'
            n = next(c.execute(q))[0]
            print('Mutations with inact=1: ' + str(n))
            # Positions affecting inactivation
            q = 'select count(idx) from ' \
                '(select distinct idx from epdata_outcomes where inact>0);'
            n = next(c.execute(q))[0]
            print('Positions with inact=1: ' + str(n))

            # Mutations affecting late
            q = 'select count(idx) from ' \
                '(select distinct idx, new from epdata_outcomes where late>0);'
            n = next(c.execute(q))[0]
            print('Mutations with late=1: ' + str(n))
            # Positions affecting late
            q = 'select count(idx) from ' \
                '(select distinct idx from epdata_outcomes where late>0);'
            n = next(c.execute(q))[0]
            print('Positions with late=1: ' + str(n))

if __name__ == '__main__':
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
