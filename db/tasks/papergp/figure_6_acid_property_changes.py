#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
import base
import numpy as np
import scipy as sp
import scipy.stats
def tasks():
    return [
        OutcomeDeltas(),
        ]
class OutcomeDeltas(base.Task):
    """
    Calculates the difference in all acidic properties for each mutation and
    tries to relate it to the outcome.

    """
    def __init__(self):
        super(OutcomeDeltas, self).__init__('outcome_deltas')
        self._set_data_subdir('papergp')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()

            # Get acid properties
            properties = [
                'average_residue_mass',
                'percent_buried_residues',
                'v_waals',
                'polarity_ranking',
                'charge',
                'hydrophobicity',
                'helix_propensity',
            ]
            pvalues = {}
            for row in c.execute('select * from acid'):
                vs = {}
                for p in properties:
                    vs[p] = row[p]
                pvalues[row['key']] = vs

            # Gather delta-properties, per outcome
            # Note that epdata_outcomes contains each mutation only once
            outcomes = ['zero', 'act', 'inact', 'late']
            ovalues = {}
            for o in outcomes:
                ovalues[o] = {}
                for p in properties:
                    ovalues[o][p] = []
            for row in c.execute('select * from epdata_outcomes'):
                old, new = row['old'], row['new']
                for o in outcomes:
                    if row[o] > 0:
                        for p in properties:
                            delta = pvalues[new][p] - pvalues[old][p]
                            ovalues[o][p].append(delta)

            # Add unchanged outcome
            outcomes += ['unchanged']
            ovalues['unchanged'] = {}
            for p in properties:
                ovalues['unchanged'][p] = []
            q = 'select * from epdata where'
            q += ' (act < 1 and inact < 1 and zero < 1 and late < 1)'
            for row in c.execute(q):
                old, new = row['old'], row['new']
                for p in properties:
                    delta = pvalues[new][p] - pvalues[old][p]
                    ovalues['unchanged'][p].append(delta)

            # Add changed outcome
            outcomes += ['changed']
            ovalues['changed'] = {}
            for p in properties:
                ovalues['changed'][p] = []
            q = 'select * from epdata where'
            q += ' (act > 0 or inact > 0 or zero > 0 or late > 0)'
            for row in c.execute(q):
                old, new = row['old'], row['new']
                for p in properties:
                    delta = pvalues[new][p] - pvalues[old][p]
                    ovalues['changed'][p].append(delta)

            # Store
            basename = 'deltas-'
            w = 0.3
            for k, o in enumerate(outcomes):
                filename = self.data_out(basename + str(1+k) +'-'+ o +'.csv')
                print('Writing ' + filename)
                with open(filename, 'w') as f:
                    c = self.csv_writer(f)
                    c.writerow(['x'] + properties)
                    n = len(ovalues[o][properties[0]])
                    iters = [iter(ovalues[o][p]) for p in properties]
                    for x in np.linspace(1+k-w, 1+k+w, n):
                        c.writerow([x] + [next(i) for i in iters])
            filename = self.data_out('deltas-labels.csv')
            print('Writing ' + filename)
            with open(filename, 'w') as f:
                f.write('x, label\n')
                for k, o in enumerate(outcomes):
                    f.write(str(k+1) + ',' + o + '\n')

            #
            # Now run a test, for each property (so independent tests!).
            #
            # Data isn't normal, so we use a Kruskal Wallis test.
            #
            # In each test, test if we can reject the null hypothesis that the
            # results in each outcome group are from the same distribution.
            #
            # This gives us a pvalue. If the pvalue is low, we can say the
            # groups are different.
            #
            print('-'*40)
            print('Comparing 5 outcomes (not including `changed`)')
            print('-'*40)
            for p in properties:
                print(p)
                # Gather samples for each outcome, not including `changed`
                groups = []
                for o in outcomes[:-1]:
                    groups.append(np.array(ovalues[o][p]))
                # Perform test
                statistic, pvalue = sp.stats.f_oneway(*groups)
                print('Anova: ' + str(statistic) + ', ' + str(pvalue))
                statistic, pvalue = sp.stats.kruskal(*groups)
                print('Kruskal-Wallis: ' + str(statistic) + ', ' + str(pvalue))
            #
            # But... samples can be in multiple changed groups, so maybe
            # compare them individually with `unchanged` as well
            #
            print('-'*40)
            print('Comparing 5 outcomes with `unchanged`')
            print('-'*40)
            for p in properties:
                print(p)
                # Gather samples for each outcome
                groups = []
                for o in outcomes:
                    groups.append(np.array(ovalues[o][p]))
                # Perform tests
                for i, o in enumerate(outcomes):
                    print('Unchanged vs ' + o)
                    statistic, pvalue = sp.stats.kruskal(groups[4], groups[i])
                    print('Kruskal-Wallis: ' + str(statistic) + ', '
                          + str(pvalue))
                print('- '*20)


if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
