#!/usr/bin/env python3
import base
def tasks():
    return [
        RegionalDensities(),
        ]
class RegionalDensities(base.Task):
    """
    Calculates the global mutation density and the (absolute and relative)
    densities in specific regions and region types.
    """
    def __init__(self):
        super(RegionalDensities, self).__init__('regional_densities')
        self._set_data_subdir('poster2014')
    def _run(self):
        print('Calculating...')
        # Get region names and positions
        position_count = 0      # Number of positions
        region_name = []        # Region name
        region_first = []       # First position in region
        region_final = []       # Final position in region
        region_size = []        # Number of positions in region
        region_map = {}         # Maps positions to regions
        region_regtype = []     # Region "regtype" values
        with base.connect() as con:
            c = con.cursor()
            q = 'select name, start, end, regtype from region order by start'
            for r in c.execute(q):
                k = len(region_name)
                region_name.append(r[0])
                region_first.append(r[1])
                region_final.append(r[2])
                region_size.append(1 + r[2] - r[1])
                for p in range(r[1], r[2] + 1):
                    region_map[p] = k
                region_regtype.append(r[3])
            position_count = r[2]
            # Number of regions
            region_count = len(region_name)
            # Number of mutations per region
            region_mutations = [0] * region_count
            mutation_count = 0
            q = 'select distinct idx, new from report where pub != "exac"'
            for r in c.execute(q):
                region_mutations[region_map[r[0]]] += 1
                mutation_count += 1
            # Get average density
            mutation_density = float(mutation_count) / position_count
            # Get mutation density and relative density, per region
            region_density = [0] * region_count
            region_reldens = [0] * region_count
            for k, count in enumerate(region_mutations):
                density = float(count) / region_size[k]
                reldens = density - mutation_density if density != 0 else 0
                region_density[k] = density
                region_reldens[k] = reldens
            # Region types
            regtype_name = []
            regtype_map = {}
            q = 'select name from regtype order by rowid'
            for k, r in enumerate(c.execute(q)):
                regtype_name.append(r[0])
                regtype_map[r[0]] = k
            # Count number of regtypes
            regtype_count = len(regtype_name)
            # Count mutations per regtype
            regtype_mutations = [0] * regtype_count
            # Count positions per regtype
            regtype_size = [0] * regtype_count
            for k, t in enumerate(region_regtype):
                t = regtype_map[t]
                regtype_mutations[t] += region_mutations[k]
                regtype_size[t] += region_size[k]
            regtype_density = [0] * regtype_count
            regtype_reldens = [0] * regtype_count
            for k, count in enumerate(regtype_size):
                density = float(regtype_mutations[k]) / count
                reldens = density - mutation_density if density != 0 else 0
                regtype_density[k] = density
                regtype_reldens[k] = reldens
            #
            # Write results
            #
            # 1. Global mutation density
            basename = 'mutation-density-global'
            filename = self.data_out(basename + '.txt')
            print('Writing info to ' + filename)
            with open(filename, 'w') as f:
                f.write('Number of positions in scn5a, mutations found, global'
                    ' mutation density.')
            filename = self.data_out(basename + '.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow([
                    'total_positions',
                    'total_mutations',
                    'total_density'])
                w.writerow([position_count, mutation_count, mutation_density])
            # 2. Mutation density in regions
            basename = 'mutation-density-regions'
            filename = self.data_out(basename + '.txt')
            print('Writing info to ' + filename)
            with open(filename, 'w') as f:
                f.write('Region name, region start, region end, region size,'
                    ' mutation density in region and mutation density relative'
                    ' to global. Finally, density and relative density in'
                    ' percentages. Relative density is calculated as'
                    ' (density in segment) / total density. Except where'
                    ' (density in segment) == 0, there, relative density is'
                    ' set to 0')
            filename = self.data_out(basename + '.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow([
                    'name',
                    'idx',
                    'first',
                    'final',
                    'count',
                    'mutations',
                    'density',
                    'reldens',
                    'pdensity',
                    'preldens',
                    ])
                for k, name in enumerate(region_name):
                    w.writerow([
                        name,
                        k,
                        region_first[k],
                        region_final[k],
                        region_size[k],
                        region_mutations[k],
                        region_density[k],
                        region_reldens[k],
                        region_density[k] * 100,
                        region_reldens[k] * 100,
                        ])   
            # 3. Mutation density in region types
            basename = 'mutation-density-regtypes'
            filename = self.data_out(basename + '.txt')
            print('Writing info to ' + filename)
            with open(filename, 'w') as f:
                f.write('Regtype name, regtype size, mutation density and'
                    ' relative mutation density.')
            filename = self.data_out(basename + '.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow([
                    'name',
                    'idx',
                    'mutations',
                    'density',
                    'reldens',
                    'pdensity',
                    'preldens',
                    ])
                for k, name in enumerate(regtype_name):
                    w.writerow([
                        name,
                        k,
                        regtype_mutations[k],
                        regtype_density[k],
                        regtype_reldens[k],
                        regtype_density[k] * 100,
                        regtype_reldens[k] * 100,
                        ])
if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
