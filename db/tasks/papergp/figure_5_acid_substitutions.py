#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
import base
import numpy as np

def tasks():
    return [
        AcidSubstitutions(),
    ]


class AcidSubstitutions(base.Task):
    """
    Creates data files for plots of the frequency with which amino acids are
    involved in substitutions, in our database.
    """
    def __init__(self):
        super(AcidSubstitutions, self).__init__('acid_substitutions')
        self._set_data_subdir('papergp')
        self._acids = None
        self._acid_map = None

    def acids(self):
        """
        Returns a list of amino acids and a reverse lookup dict.

        (So a list [A, R, N, ...] and a dict {A:0, R:1, N:2, ...}).
        """
        if self._acids is None:
            if False:
                acids = []
                acid_map = {}
                with base.connect() as con:
                    c = con.cursor()
                    q = 'select key from acid order by rowid'
                    for k, row in enumerate(c.execute(q)):
                        acids.append(row['key'])
                        acid_map[row['key']] = k
                self._acids = acids
                self._acid_map = acid_map
            else:
                self._acids = 'KDERHQNSPTGACWFLIMYV'
                assert(len(self._acids) == 20)
                self._acid_map = dict(
                    zip(self._acids, range(len(self._acids))))
        return self._acids, self._acid_map

    def expected(self, simple_weights=False):
        """
        Returns a 2d matrix of expected amino acid substitutions ratios.

        Uses weights based on single nucleotide substitutions.

        By default, these take into account rates derived from the human
        genome. To disable this, set simple_weights = True.
        """
        acids, acid_map = self.acids()
        n = len(acids)

        matrix = np.zeros((n, n))
        with base.connect() as con:
            c = con.cursor()
            q = 'select old, new, '
            q += 'simple_weight as weight' if simple_weights else 'weight'
            q += ' from mutation_possible'
            for k, row in enumerate(c.execute(q)):
                old = acid_map[row['old']]
                new = acid_map[row['new']]
                matrix[old, new] += row['weight']
                if old == new:
                    print(row['old'], row['new'])

        return matrix / np.sum(matrix)

    def observed(self):
        """
        Returns a matrix of observed amino acid substituion ratios.
        """
        acids, acid_map = self.acids()
        n = len(acids)

        matrix = np.zeros((n, n), dtype=float)
        with base.connect() as con:
            c = con.cursor()
            q = 'select distinct old, idx, new from report where pub != "exac"'
            for k, row in enumerate(c.execute(q)):
                old = acid_map[row['old']]
                new = acid_map[row['new']]
                matrix[old, new] += 1

        return matrix / np.sum(matrix)

    def calculate(self, basename, simple_weights):

        # Get list of acids, and a mapping from acid to list index
        acids, acid_map = self.acids()
        n = len(acids)

        # Get matrix of expected amino acid substitution ratios
        exp = self.expected()

        # Get matrix of observed amino acid substitution ratios
        obs = self.observed()

        # Store positions of
        #  - not observed, not expected
        #  - observed, not expected
        #  - expected, not observed
        not_obs_not_exp = (obs == 0) * (exp == 0)
        obs_not_exp = (obs != 0) * (exp == 0)
        exp_not_obs = (obs == 0) * (exp != 0)
        obs_exp = (obs != 0) * (exp != 0)
        assert(not np.any(not_obs_not_exp * obs_not_exp))
        assert(not np.any(not_obs_not_exp * exp_not_obs))
        assert(not np.any(obs_not_exp * exp_not_obs))

        # Calculate observed vs expected ratios
        with np.errstate(all='ignore'):
            ratios = obs / exp

        # Find lowest and highest (finite) ratio
        rmin = np.min(obs[obs_exp] / exp[obs_exp])
        rmax = np.max(obs[obs_exp] / exp[obs_exp])

        # Fill in special values for ratios
        ratios[not_obs_not_exp] = 1
        ratios[obs_not_exp] = rmax
        ratios[exp_not_obs] = rmin

        # Write file with ratios
        filename = self.data_out(basename + '.csv')
        print('Writing ' + filename)
        with open(filename, 'w') as f:
            w = self.csv_writer(f)
            for row in ratios:
                w.writerow(row)

        # Write exp-not-obs to file
        filename = self.data_out(basename + '-exp-not-obs.csv')
        print('Writing ' + filename)
        with open(filename, 'w') as f:
            w = self.csv_writer(f)
            w.writerow(('epx-not-obs-x', 'exp-not-obs-y'))
            for i in range(n):
                for j in range(n):
                    if exp_not_obs[i, j]:
                        w.writerow((0.5 + j, 19.5 - i))

        # Write obs-not-exp to file
        filename = self.data_out(basename + '-obs-not-exp.csv')
        print('Writing ' + filename)
        with open(filename, 'w') as f:
            w = self.csv_writer(f)
            w.writerow(('obs-not-exp-x', 'obs-not-exp-y'))
            for i in range(n):
                for j in range(n):
                    if obs_not_exp[i, j]:
                        w.writerow((0.5 + j, 19.5 - i))

        # Write not-obs-not-exp to file
        filename = self.data_out(basename + '-not-obs-not-exp.csv')
        print('Writing ' + filename)
        with open(filename, 'w') as f:
            w = self.csv_writer(f)
            w.writerow(('not-obs-not-exp-x', 'not-obs-not-exp-y'))

            for i in range(n):
                for j in range(n):
                    if not_obs_not_exp[i, j]:
                        w.writerow((0.5 + j, 19.5 - i))

        # Gather marginals
        # Note: No imputations needed here!
        # Indices in matrix are matrix[old, new]
        # So each row is for a single old acid, each column for a single new
        # Summing over axis=0 gives sum per column (new)
        # Summing over axis=1 gives sum per row (old)
        marginals_old = np.sum(obs, axis=1) / np.sum(exp, axis=1)
        marginals_new = np.sum(obs, axis=0) / np.sum(exp, axis=0)

        # Write file with margins
        filename = self.data_out(basename + '-marginals.csv')
        print('Writing ' + filename)
        # This also needs x and y-axis positions for the histograms
        xax = 0.5 + np.arange(20)
        yax = 19.5 - np.arange(20)
        with open(filename, 'w') as f:
            w = self.csv_writer(f)
            w.writerow((
                'marg-acid', 'marg-old', 'marg-new', 'marg-x', 'marg-y'))
            for i, acid in enumerate(acids):
                w.writerow((
                    acid, marginals_old[i], marginals_new[i], xax[i], yax[i]))

    def _run(self):

        self.calculate('substitutions-1-weighted', False)


if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
