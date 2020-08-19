#!/usr/bin/env python3
import base
import numpy as np
def tasks():
    return [
        ScoreMeanStd(),
        ]
class ScoreMeanStd(base.Task):
    """
    Calculates mean and standard averages of the number of mutations, hse
    score and dom score. A comparison is made between hse/dom scores of
    positions with and without mutations.
    """
    def __init__(self):
        super(ScoreMeanStd, self).__init__('score_mean_std')
        self._set_data_subdir('poster2014')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            # Get positions (may have gaps!)
            idx = []
            for r in c.execute('select idx from scn5a order by idx'):
                idx.append(r[0])
            idx = np.array(idx)
            # Get mutations for each position
            q = 'select distinct idx, new from report where pub != "exac"'
            mut = np.zeros(idx.shape)
            for r in c.execute(q):
                mut[r[0] - 1] = 1  # Positions start at 1
            # Get Human-squid-eel and domain alignment score
            hse = np.zeros(idx.shape, dtype=float)
            dom = np.zeros(idx.shape, dtype=float)
            q = 'select idx, hse, dom from conservedness order by idx'
            for k, r in enumerate(c.execute(q)):
                assert(r[0] -1 == k) # Score should be stored for each idx
                hse[k] = r[1]
                dom[k] = r[2]
            #
            # 1. Overal mean mutation count and hse/dom scores
            #    (Text output only)
            #
            hse_mean = np.mean(hse)
            hse_stdd = np.std(hse)
            dom_mean = np.mean(dom)
            dom_stdd = np.std(dom)
            print('Mean hse: ' + str(hse_mean) +', std: '+ str(hse_stdd))
            print('Mean dom: ' + str(dom_mean) +', std: '+ str(dom_stdd))
            #
            # 2. Position and dom/hse scores for positions with and without
            #    mutations.
            #    (Text output only)
            #
            idx_idx = idx[mut > 0]
            hse_idx = hse[mut > 0]
            dom_idx = dom[mut > 0]
            idx_neg = idx[mut == 0]
            hse_neg = hse[mut == 0]
            dom_neg = dom[mut == 0]
            hse_idx_mean = np.mean(hse_idx)
            hse_idx_stdd = np.std(hse_idx)
            dom_idx_mean = np.mean(dom_idx)
            dom_idx_stdd = np.std(dom_idx)
            hse_neg_mean = np.mean(hse_neg)
            hse_neg_stdd = np.std(hse_neg)
            dom_neg_mean = np.mean(dom_neg)
            dom_neg_stdd = np.std(dom_neg)
            print('HSE score:')
            print('  Mean, with mutations: ' + str(hse_idx_mean)
                + ', std: ' + str(hse_idx_stdd))
            print('  Mean, no mutations  : ' + str(hse_neg_mean)
                + ', std: ' + str(hse_neg_stdd))
            print('DOM score:')
            print('  Mean, with mutations: ' + str(dom_idx_mean)
                + ', std: ' + str(dom_idx_stdd))
            print('  Mean, no mutations  : ' + str(dom_neg_mean)
                + ', std: ' + str(dom_neg_stdd))
            #
            # 3. HSE and DOM score for positions with and without mutations
            #    (For use in a box-plot)
            #
            basename = 'score-with-mutations'
            filename = self.data_out(basename + '.txt')
            print('Writing info to ' + filename)
            with open(filename, 'w') as f:
                f.write(
                    'Scores for positions with mutations (idx, hse, dom)')
            filename = self.data_out(basename + '.csv') 
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                c = self.csv_writer(f)
                c.writerow(['position', 'hse-score', 'dom-score'])
                h = iter(hse_idx)
                d = iter(dom_idx)
                for p in idx_idx:
                    c.writerow([p, next(h), next(d)])
            basename = 'score-without-mutations'
            filename = self.data_out(basename + '.txt')
            print('Writing info to ' + filename)
            with open(filename, 'w') as f:
                f.write(
                    'Scores for positions without mutations (idx, hse, dom)')
            filename = self.data_out(basename + '.csv') 
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                c = self.csv_writer(f)
                c.writerow(['position', 'hse-score', 'dom-score'])
                h = iter(hse_neg)
                d = iter(dom_neg)
                for p in idx_neg:
                    c.writerow([p, next(h), next(d)])
            # Write labels used to create box plots
            basename = 'score-with-without-mutations-labels'
            filename = self.data_out(basename + '.csv')
            print('Writing label info to ' + filename)
            with open(filename, 'w') as f:
                c = self.csv_writer(f)
                c.writerow(['HSE-'])
                c.writerow(['HSE+'])
                c.writerow(['DOM-'])
                c.writerow(['DOM+'])
if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
