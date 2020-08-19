#!/usr/bin/env python3
import os
import base
import numpy as np
def tasks():
    return [
        MutationDimosLocations(),
        ]
class MutationDimosLocations(base.Task):
    """
    Retrieves the location of mutations in SCN5A, based on the homology
    modeling by Dimos.
    """
    def __init__(self):
        super(MutationDimosLocations, self).__init__(
            'mutation_dimos_locations')
        self._set_data_subdir('position3d')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            #
            # 1. Create files showing the physical locations of positions with
            #    epdata, no epdata and no mutations (only positions present in
            #    the homology (i.e. no linkers)
            #
            # Get all positions with mutations (no exac)
            q = 'select distinct idx from report where pub != "exac"'
            mutations = set()
            for row in c.execute(q):
                mutations.add(row['idx'])
            # Get all positions with epdata
            epdata = set()
            for row in c.execute('select distinct idx from epdata'):
                epdata.add(row['idx'])
            # Write dimos locations of SCN5A mutations, where known
            file1 = self.data_out('dimos-locations-epdata.csv')
            file2 = self.data_out('dimos-locations-mutation.csv')
            file3 = self.data_out('dimos-locations-free.csv')
            try:
                f1 = open(file1, 'w')
                f2 = open(file2, 'w')
                f3 = open(file3, 'w')
                c1 = self.csv_writer(f1)
                c2 = self.csv_writer(f2)
                c3 = self.csv_writer(f3)
                data = ['idx','x','y','z','r','t']
                c1.writerow(data)
                c2.writerow(data)
                c3.writerow(data)                
                print('Writing data to ' + file1)
                print('            and ' + file2)
                print('            and ' + file3)
                for row in c.execute('select * from scn5a_dimos_locations'):
                    # Store data
                    idx = row['idx']
                    data = [idx, row['x'], row['y'],row['z'],row['r'],row['t']]
                    if idx in epdata:
                        c1.writerow(data)
                    elif idx in mutations:
                        c2.writerow(data)
                    else:
                        c3.writerow(data)
            finally:
                f1.close()
                f2.close()
                f3.close()
            #
            # 2. Create a file with dimos positions of mutations and the
            #    associated dvi and dva
            #
            # Get midpoint shifts
            q = 'select * from epdata_filtered'
            q += ' where dva is not null and dvi is not null'
            names = {}
            dvi = {}
            dva = {}
            for row in c.execute(q):
                names[row['idx']] = row['old']+str(row['idx'])+row['new']
                dvi[row['idx']] = row['dvi']
                dva[row['idx']] = row['dva']
            # Write file with distance to pore and midpoint shifts
            file1 = self.data_out('voltage-shift-dimos-locations.csv')
            print('Writing data to ' + file1)
            with open(file1, 'w') as f1:
                c1 = self.csv_writer(f1)
                c1.writerow([
                    'name',
                    'r',
                    'dva',
                    'dvi',
                    'dva_abs',
                    'dvi_abs',
                    'sum_abs',
                    'window',
                    ])
                for row in c.execute('select * from scn5a_dimos_locations'):
                    idx = row['idx']
                    # Get epdata or skip
                    try:
                        name = names[idx]
                        da = dva[idx]
                        di = dvi[idx]
                    except KeyError:
                        continue
                    c1.writerow([
                        name,
                        row['r'],
                        da,
                        di,
                        abs(di),
                        abs(da),
                        abs(di) + abs(di),
                        di - da,
                        ])
            #
            # 3. Create a file with dimos positions, grouped by SCN5A region
            #
            # Get regions, scn5a idx to region mapping
            regions = []
            scn5a_regions = {}
            for row in c.execute('select * from region order by start'):
                regions.append(row['name'])
                for idx in range(row['start'], 1 + row['end']):
                    scn5a_regions[idx] = row['name']
            # Create files
            path = self.data_out('dimos_location_regions')
            if not os.path.isdir(path):
                os.makedirs(path)
            files = []
            csvs = {}
            try:
                # Open file per region
                for region in regions:
                    filename = region.replace(' ', '-')
                    filename = os.path.join(path, region + '.csv')
                    print('Writing data to ' + filename)
                    f = open(filename, 'w')
                    files.append(f)
                    csv = self.csv_writer(f)
                    csvs[region] = csv
                    csv.writerow(['idx', 'x', 'y', 'z'])
                # Get and write data
                q = 'select * from scn5a_dimos_locations order by idx'
                for row in c.execute(q):
                    idx = row['idx']
                    # Write to correct file
                    csv = csvs[scn5a_regions[idx]]
                    csv.writerow([idx, row['x'], row['y'], row['z']])
            finally:
                for f in files:
                    f.close()
if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()    
