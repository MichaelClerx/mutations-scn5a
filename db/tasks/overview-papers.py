#!/usr/bin/env python3
#
# Returns a list of papers with several mutations.
#
import base
def tasks():
    """
    Returns a list of papers with several mutations.
    """
    return [
        OverviewPapers(),
        ]
class OverviewPapers(base.Task):
    def __init__(self):
        super(OverviewPapers, self).__init__('overview_papers')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            q = 'select pub, count(idx) as muts from report group by pub'
            q += ' order by muts desc'
            for row in c.execute(q):
                if row['muts'] < 5:
                    break
                print(str(row['muts']) + ' :: ' + row['pub'])


if __name__ == '__main__':
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
