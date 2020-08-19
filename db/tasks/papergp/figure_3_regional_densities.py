#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
import base
import numpy as np


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
        super(RegionalDensities, self).__init__(
            'regional_densities')
        self._set_data_subdir('papergp')

    def _run(self):
        with base.connect() as con:
            c = con.cursor()

            #
            # Global mutation density
            #

            # Get total number of positions
            q = 'select count(idx) from scn5a'
            total_length = c.execute(q).fetchone()[0]

            # Get total number of positions with a (non exac) mutation
            q = 'select count(idx) from mutation_no_exac'
            total_count = c.execute(q).fetchone()[0]

            # Global mutation density
            global_density = total_count / total_length


            #
            # Mutation density per domain
            #

            # Domain names
            domain_names = [
                r['name'] for r in c.execute('select name from domain')]

            # Domain lengths
            domain_lengths = []
            for name in domain_names:
                q = 'select sum(length) from region'
                q += ' where domain = "' + name + '"'
                domain_lengths.append(c.execute(q).fetchone()[0])

            # Number of mutations per domain
            domain_count = []
            for name in domain_names:
                q = 'select count(idx)'
                q += ' from mutation_no_exac_annotated'
                q += ' where domain = "' + name + '"'
                domain_count.append(c.execute(q).fetchone()[0])

            # Mutation density per domain
            domain_density = np.array(domain_count) / np.array(domain_lengths)

            # Relative mutation density per domain
            domain_reldens = domain_density - global_density

            # Write file
            filename = self.data_out('density-1-per-domain.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow([
                    'xaxis',
                    'xlabel',
                    'density',
                    'relative-density',
                ])
                for k, name in enumerate(domain_names):
                    w.writerow([
                        k + 1,
                        name,
                        domain_density[k],
                        domain_reldens[k],
                    ])

            #
            # Mutation density per region type
            #

            # Region type names
            regtype_names = [
                r['name'] for r in c.execute('select name from regtype')]

            # Regtype lengths
            regtype_lengths = []
            for name in regtype_names:
                q = 'select sum(length) from region'
                q += ' where regtype = "' + name + '"'
                regtype_lengths.append(c.execute(q).fetchone()[0])

            # Number of mutations per regtype
            regtype_count = []
            for name in regtype_names:
                q = 'select count(idx)'
                q += ' from mutation_no_exac_annotated'
                q += ' where regtype = "' + name + '"'
                regtype_count.append(c.execute(q).fetchone()[0])

            # Mutation density per regtype
            regtype_density = np.array(regtype_count)/np.array(regtype_lengths)

            # Relative mutation density per regtype
            regtype_reldens = regtype_density - global_density

            # Write file
            filename = self.data_out('density-2-per-regtype.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow([
                    'xaxis',
                    'xlabel',
                    'density',
                    'relative-density',
                ])
                for k, name in enumerate(regtype_names):
                    w.writerow([
                        k + 1,
                        name,
                        regtype_density[k],
                        regtype_reldens[k],
                    ])


            #
            # Mutation density per region
            #

            # Region names
            q = 'select name from region order by start'
            region_names = [r['name'] for r in c.execute(q)]

            # Region lengths
            region_lengths = []
            for name in region_names:
                q = 'select length from region'
                q += ' where name = "' + name + '"'
                region_lengths.append(c.execute(q).fetchone()[0])

            # Number of mutations per region
            region_count = []
            for name in region_names:
                q = 'select count(idx)'
                q += ' from mutation_no_exac_annotated'
                q += ' where region = "' + name + '"'
                region_count.append(c.execute(q).fetchone()[0])

            # Mutation density per region
            region_density = np.array(region_count) / np.array(region_lengths)

            # Relative mutation density per regtype
            region_reldens = region_density - global_density

            # Write file
            filename = self.data_out('density-3-per-region.csv')
            print('Writing data to ' + filename)
            with open(filename, 'w') as f:
                w = self.csv_writer(f)
                w.writerow([
                    'xaxis',
                    'xlabel',
                    'density',
                    'relative-density',
                ])
                for k, name in enumerate(region_names):
                    w.writerow([
                        k + 1,
                        name,
                        region_density[k],
                        region_reldens[k],
                    ])

if __name__ == '__main__':
    t = base.TaskRunner()
    t.add_tasks(tasks())
    t.run()
