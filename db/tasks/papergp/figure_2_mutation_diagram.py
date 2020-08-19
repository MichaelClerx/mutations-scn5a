#!/usr/bin/env python
from __future__ import print_function
import os
import base
import numpy as np
def tasks():
    return [
        MutationDiagram(),
        ]
class MutationDiagram(base.Task):
    """
    Writes CSV files to create a diagram of SCN5A, isoform a

    Writes several files:

    ``diagram.csv``
        The locations in the diagram of every position in SCN5A, isoform a
    ``diagram-1-exac.csv``
        The locations in the diagram of every position where a mutation is
        known from exac, but not from the literature.
    ``diagram-2-no-epdata.csv``
        The locations in the diagram of every position reported in the
        literature where one or more mutations were reported, but no epdata was
        available.
    ``diagram-3-epdata-no-change.csv``
        The locations in the diagram of every position where one or more
        mutations were reported, epdata was available for one or more mutations
        but no changes were seen.
    ``diagram-4-epdata-change.csv``
        The locations in the diagram of every position where one or more
        mutations were reported and epdata was available for one or more
        mutations indicating a change in cellular EP (either action,
        inactivation, late INa, or zero current).

    """
    def __init__(self):
        super(MutationDiagram, self).__init__('mutation_diagram')
        self._set_data_subdir('papergp')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()

            #
            # Retrieve all locations
            #
            indices = []
            q = 'select idx from scn5a order by idx'
            for row in c.execute(q):
                indices.append(row['idx'])
            locations = {}
            for row in c.execute('select * from scn5a_diagram order by idx'):
                locations[row['idx']] = (row['x'], row['y'])
            if len(locations) != len(indices):
                raise Exception('Number of locations in scn5a diagram does'
                    ' not match number of indices in scn5a isoform a.')

            #
            # Create file 1: All locations
            #
            filename = self.data_out('diagram.csv')
            print('Writing ' + filename)
            with open(filename, 'w') as f:
                csv = self.csv_writer(f)
                csv.writerow(['idx', 'x', 'y'])
                for idx in indices:
                    x,y = locations[idx]
                    csv.writerow([idx, x, y])

            #
            # Load mutation data
            #
            mutations = set()
            q = 'select distinct idx from mutation_no_exac'
            for row in c.execute(q):
                mutations.add(row['idx'])

            # Get mutations known only from exac
            exac = set()
            q = 'select distinct idx from report where pub = "exac";'
            for row in c.execute(q):
                exac.add(row['idx'])
            exac -= mutations

            # Load positions with epdata, but no changes
            epdata = set()
            q = 'select idx from epdata_annotated'
            for row in c.execute(q):
                epdata.add(row['idx'])

            # Load positions with epdata and known changes
            change_known = set()
            q = 'select idx from epdata_annotated'
            q += ' where (zero>0 or act>0 or inact>0 or late>0) order by idx'
            for row in c.execute(q):
                change_known.add(row['idx'])

            # Get positions with epdata but no known changes
            #no_change_known = epdata - change_known
            no_change_known = set()
            q = 'select idx from epdata_annotated'
            q += ' where (zero<1 and act<1 and inact<1 and late<1) order by idx'
            for row in c.execute(q):
                no_change_known.add(row['idx'])



            # Get positions with no known epdata
            no_epdata_known = mutations - epdata

            #
            # Create extra file 1: Known only from exac
            #
            filename = self.data_out('diagram-1-exac.csv')
            print('Writing ' + filename)
            with open(filename, 'w') as f:
                csv = self.csv_writer(f)
                csv.writerow(['idx', 'x', 'y'])
                for idx in sorted(exac):
                    x,y = locations[idx]
                    csv.writerow([idx, x, y])
            #
            # Create extra file 2: No known EP data
            #
            filename = self.data_out('diagram-2-no-epdata.csv')
            print('Writing ' + filename)
            with open(filename, 'w') as f:
                csv = self.csv_writer(f)
                csv.writerow(['idx', 'x', 'y'])
                for idx in sorted(no_epdata_known):
                    x,y = locations[idx]
                    csv.writerow([idx, x, y])
            #
            # Create extra file 3: EP data known, no changes observed
            #
            filename = self.data_out('diagram-3-epdata-no-change.csv')
            print('Writing ' + filename)
            with open(filename, 'w') as f:
                csv = self.csv_writer(f)
                csv.writerow(['idx', 'x', 'y'])
                for idx in sorted(no_change_known):
                    x,y = locations[idx]
                    csv.writerow([idx, x, y])
            #
            # Create extra file 4: EP data known, changes observed
            #
            filename = self.data_out('diagram-4-epdata-change.csv')
            print('Writing ' + filename)
            with open(filename, 'w') as f:
                csv = self.csv_writer(f)
                csv.writerow(['idx', 'x', 'y'])
                for idx in sorted(change_known):
                    x,y = locations[idx]
                    csv.writerow([idx, x, y])
if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
