#!/usr/bin/env python3
import os
import base
import numpy as np
def tasks():
    return [
        CoverDiagram(),
        ]
class CoverDiagram(base.Task):
    """
    Writes a csv file of the diagrammatic locations of SCN5A, to use when
    creating a cover diagram for the 3d positions.
    """
    def __init__(self):
        super(CoverDiagram, self).__init__('cover_diagram')
        self._set_data_subdir('position3d')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            # Retrieve all locations
            indices = []
            q = 'select * from scn5a_isoform_b order by idx'
            for row in c.execute(q):
                indices.append(row['idx'])
            locations = {}
            for row in c.execute('select * from scn5a_diagram order by idx'):
                locations[row['idx']] = (row['x'], row['y'])
            # Write to file
            filename = self.data_out('diagram_isoform_b.csv')
            print('Writing ' + filename)
            with open(filename, 'w') as f:
                csv = self.csv_writer(f)
                csv.writerow(['idx', 'x', 'y'])
                for idx in indices:
                    x,y = locations[idx]
                    csv.writerow([idx, x, y])
if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()    
