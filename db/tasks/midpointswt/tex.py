#!/usr/bin/env python3
#
# Create table in tex
#
import base
def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        MidpointsTex(),
        ]
class MidpointsTex(base.Task):
    def __init__(self):
        super(MidpointsTex, self).__init__('midpoints_tex')
        self._set_data_subdir('midpointswt')
    
    def _run(self):
        # Collect tex references
        refs = {}
        with base.connect() as con:
            c = con.cursor()
            q = 'select key, tex from publication_tex'
            for k, row in enumerate(c.execute(q)):
                refs[row['key']] = row['tex']
        # Create table file
        filename = self.data_out('midpoint-table.tex')
        fields = [
            'pub',
            'va',
            'na',
            'stda',
            'vi',
            'ni',
            'stdi',
            'sequence',
            'cell',
            'beta1',
            ]
        # Sequence formatting
        def seq(s):
            if s == 'astar':
                return 'a*'
            elif s == 'bstar':
                return 'b*'
            elif s is None:
                return '?'
            return s
        # Create table
        with open(filename, 'w') as f:
            # Header
            size = 'footnotesize'
            f.write('\\begin{' + size + '}\n')
            f.write('\\startrowcolors\n')
            f.write('\\begin{longtable}{p{5cm}|lll|lll|lll}\n')
            f.write('\\caption{\\label{midpoints}Midpoints} \\\\\n')
            f.write('\\hline\n')
            f.write('Publication')
            f.write(' & $V_a$ & $\sigma_a$  & $n_a$')
            f.write(' & $V_i$ & $\sigma_i$  & $n_i$')  
            f.write(' & Cell & $\\alpha$ & $\\beta1$ \\\\\n')
            f.write('\\hline\n')
            f.write('\\endfirsthead')
            f.write('\\hline\n')
            f.write('\\rowcolor{white}\n')
            f.write('Publication')
            f.write(' & $V_a$ & $\sigma_a$  & $n_a$')
            f.write(' & $V_i$ & $\sigma_i$  & $n_i$')  
            f.write(' & Cell & $\\alpha$ & $\\beta1$ \\\\\n')
            f.write('\\hline\n')
            f.write('\\endhead\n')
            f.write('\\hline\n')
            f.write('\\endfoot\n')
            # Body
            form = '{:.3g}'
            with base.connect() as con:
                c = con.cursor()
                q = 'select ' + ', '.join(fields) + ' from midpoints_wt'
                for k, row in enumerate(c.execute(q)):
                    x = []
                    x.append('\\citet{' + refs[row['pub']] + '}')
                    if row['na'] != 0:
                        x.append(form.format(row['va']))
                        x.append(form.format(row['stda']))
                        x.append(form.format(row['na']))
                    else:
                        x.append('&&')
                    if row['ni'] != 0:
                        x.append(form.format(row['vi']))
                        x.append(form.format(row['stdi']))
                        x.append(form.format(row['ni']))
                    else:
                        x.append('&&')
                    x.append(row['cell'].replace('Oocyte', 'Ooc.'))
                    x.append(seq(row['sequence']))
                    x.append(row['beta1'])
                    f.write(' & '.join(x) + ' \\\\\n')
            # Footer
            f.write('\\end{longtable}\n')
            f.write('\\end{' + size + '}\n')
if __name__ == '__main__':
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
