#!/usr/bin/env python3
import os
import base
import numpy as np
def tasks():
    return [
        DimosCoverDiagram(),
        ]
class DimosCoverDiagram(base.Task):
    """
    Retrieves the diagram locations of acids present in Dimos' homology model.
    """
    def __init__(self):
        super(DimosCoverDiagram, self).__init__('dimos_cover_diagram')
        self._set_data_subdir('position3d')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            # Get scn5a isoform b indices
            indices = []
            q = 'select * from scn5a_isoform_b order by idx'
            for row in c.execute(q):
                indices.append(row['idx'])
            isoform_b = set(indices)
            # Get a map from index to diagram location
            locations = {}
            for row in c.execute('select * from scn5a_diagram order by idx'):
                locations[row['idx']] = (row['x'], row['y'])
            # Get scn5a indices matched to an acid in the model, write to file
            filename = self.data_out('diagram-dimos-cover.csv')
            with open(filename, 'w') as f:
                csv = self.csv_writer(f)
                csv.writerow(('idx', 'x', 'y'))
                q = 'select idx from scn5a_dimos_locations order by idx;'
                for row in c.execute(q):
                    idx = row['idx']
                    if idx in isoform_b:
                        x, y = locations[idx]
                        csv.writerow((idx, x, y))
if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()    
