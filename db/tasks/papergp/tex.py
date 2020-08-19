#!/usr/bin/env python3
#
# Create EPData table in latex
#
import base

def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        EPDataTex(),
        ]


class EPDataTex(base.Task):

    def __init__(self):
        super(EPDataTex, self).__init__('epdata_tex')
        self._set_data_subdir('papergp')

    def _run(self):
        # Collect tex references
        refs = {}
        with base.connect() as con:
            c = con.cursor()
            q = 'select key, tex from publication_tex'
            for k, row in enumerate(c.execute(q)):
                refs[row['key']] = row['tex']
        # Create table file
        filename = self.data_out('epdata-table.tex')
        fields = [
            'pub',
            'old',
            'idx',
            'new',
            'dva',
            'dvi',
            'zero',
            'act',
            'inact',
            'late',
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
            elif s == 'achen':
                return 'a**'
            elif s is None:
                return ''
            return s
        def cell(c):
            if c in ['HEK', 'CHO']:
                return c
            elif c == 'Mouse myocyte':
                return 'MM'
            elif c == 'Oocyte':
                return 'Ooc.'
            elif c is None:
                return ''
            return c
        def yesno(x):
            return 'yes' if x == 1 else ('no' if x == -1 else '')
        # Create table
        with open(filename, 'w') as f:
            # Header
            size = 'tiny'
            f.write('\\begin{' + size + '}\n')
            f.write('\\startrowcolors\n')
            f.write('\\begin{longtable}{p{4cm}|l|llll|ll|lll}\n')
            f.write('\\caption{\\label{tab:epdata}EP Data} \\\\\n')
            f.write('\\hline\n')
            f.write('Publication')
            f.write(' & Mutation')
            f.write(' & Act. & Inact. & Late & Zero')
            f.write(' & ${\Delta}V_a$ & ${\Delta}V_i$')
            f.write(' & Cell & $\\alpha$ & $\\beta1$ \\\\\n')
            f.write('\\hline\n')
            f.write('\\endfirsthead')
            f.write('\\hline\n')
            f.write('\\rowcolor{white}\n')
            f.write('Publication')
            f.write(' & Mutation')
            f.write(' & Act. & Inact. & Late & Zero')
            f.write(' & ${\Delta}V_a$ & ${\Delta}V_i$')
            f.write(' & Cell & $\\alpha$ & $\\beta1$ \\\\\n')
            f.write('\\hline\n')
            f.write('\\endhead\n')
            f.write('\\hline\n')
            f.write('\\endfoot\n')
            # Body
            form = '{:.3g}'
            with base.connect() as con:
                c = con.cursor()
                q = 'select ' + ', '.join(fields) + ' from epdata'
                q += ' order by idx, new'
                for k, row in enumerate(c.execute(q)):
                    x = []
                    x.append('\\citet{' + refs[row['pub']] + '}')
                    x.append(row['old'] + str(row['idx']) + row['new'])
                    x.append(yesno(row['act']))
                    x.append(yesno(row['inact']))
                    x.append(yesno(row['late']))
                    x.append(yesno(row['zero']))
                    x.append(
                        '' if row['dva'] is None else form.format(row['dva']))
                    x.append(
                        '' if row['dvi'] is None else form.format(row['dvi']))
                    x.append(cell(row['cell']))
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
