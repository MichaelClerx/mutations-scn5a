#!/usr/bin/env python3
#
# Creates a single file showing known ephys data along with amino acid
# properties and other genotype information
#
import base
import numpy as np


def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        WekaInputCSV(),
        ]


class WekaInputCSV(base.Task):
    def __init__(self):
        super(WekaInputCSV, self).__init__('weka_input_csv')
        self._set_data_subdir('weka_csv')
        self._cached_positions = None
        self._cached_position_indices = None
        self._cached_residues = None
        self._cached_acid_properties = None

    def _acid_properties(self, connection):
        """
        Returns a dict with all numerical amino acid properties.

        The dict keys are one letter amino acid abbreviations. The values are
        dicts containing the entries listed below.

        average_residue_mass
            #TODO DESCRIBE
        percent_buried_residues
            #TODO DESCRIBE
        v_residues
            #TODO DESCRIBE
        v_waals
            #TODO DESCRIBE
        polarity_ranking
            #TODO DESCRIBE
        kovacs_hydrophobicity
            Hydrophobicity according to Kovacs et al. 2006
        monera_hydrophobicity
            Hydrophobicity according to Monera et al. 1995
        pace_helix_propensity
            Helix propensity according to Pace et al. 1998

        Returns the created dict of dicts. To retrieve some data for the
        returned dict ``a``, use ``a[acid][property]``.
        """
        if self._cached_acid_properties is None:
            # Read-only dict structure
            import collections
            class ReadOnlyDict(collections.Mapping):
                def __init__(self, data):
                    self._data = data
                def __getitem__(self, key):
                    return self._data[key]
                def __len__(self):
                    return len(self._data)
                def __iter__(self):
                    return iter(self._data)
            # Load properties
            print('Loading acid properties')
            c = connection.cursor()
            acid_properties = {}
            for row in c.execute('select * from acid'):
                p = {}
                for x in self._acid_property_names():
                    p[x] = row[x]
                acid_properties[row['key']] = p
            self._cached_acid_properties = acid_properties
        return self._cached_acid_properties

    def _acid_property_names(self):
        return [
            'average_residue_mass',
            'percent_buried_residues',
            #'v_residues',  # Tested, this is very similar to v/d waals
            'v_waals',
            'polarity_ranking',
            'charge',
            'hydrophobicity',
            #'monera_hydrophobicity', # Tested, very similar to kovacs, plus
            # kovacs is an update of the monera scale, same senior author
            'helix_propensity',
            ]

    def _positions(self, connection):
        """
        Returns a list of all positions in SCN5A, isoform b.
        """
        if self._cached_positions is None:
            print('Loading SCN5A positions')
            c = connection.cursor()
            q = 'select idx from scn5a_isoform_b order by idx ASC;'
            self._cached_positions = [row['idx'] for row in c.execute(q)]
        return list(self._cached_positions)

    def _position_indices(self, connection):
        """
        Return a dictionary mapping SCN5A positions (which are labels) to array
        indices in the position array.
        """
        if self._cached_position_indices is None:
            positions = self._positions(connection)
            self._cached_position_indices = {}
            for k, p in enumerate(positions):
                self._cached_position_indices[p] = k
        return dict(self._cached_position_indices)

    def _residues(self, connection):
        """
        Returns a list of all amino acids making up SCN5A, isoform b (in the
        correct order, without gaps).
        """
        if self._cached_residues is None:
            print('Loading SCN5A residues')
            c = connection.cursor()
            q = 'select acid from scn5a_isoform_b order by idx ASC;'
            self._cached_residues = [row['acid'] for row in c.execute(q)]
        return list(self._cached_residues)

    def _conservedness(self, connection, position_properties, dom=True,
            hse=True):
        """
        Adds conservedness scores to the position properties.

        dom
            Score based on an alignment of all four channel domains.
        hse
            Score based on the human sodium channels, augmented with a squid
            and an electrical sequence.

        """
        scores = []
        if dom:
            scores.append('dom')
        if hse:
            scores.append('hse')
        if not scores:
            return
        print('Loading conservedness scores')
        c = connection.cursor()
        for row in c.execute('select * from conservedness'):
            try:
                p = position_properties[row['idx']]
            except KeyError:
                continue
            for x in scores:
                p[x] = row[x]

    def _navab_coordinates(self, connection, position_properties,
            remove_unlisted=True):
        """
        Adds NavAb-based x,y,z,r and t coordinates to the position properties,
        wherever they can be found.

        If ``remove_unlisted`` is set to ``True``, it removes all positions
        for which no coordinates could be found.

        Added keys:

        x
            The x-coordinate (which points into the membrane plane), relative
            to the channel center.
        y
            The y-coordinate (which points into the membrane plane), relative
            to the channel center.
        z
            The z-coordinate (which points towards the extracellular medium),
            relative to the channel center.
        r
            The distance to the z-axis.
        t
            The angle between the x and y axes.

        """
        print('Loading NavAb-based coordinates')
        print('*not* using interpolated dataset')
        c = connection.cursor()
        q  = 'select navab_to_scn5a.scn5a, navab_locations.*'
        q += 'from navab_locations inner join navab_to_scn5a'
        q += ' on navab_locations.key = navab_to_scn5a.navab;'
        keep = set()
        for row in c.execute(q):
            p = positions_properties[row['scn5a']]
            for x in ['x', 'y', 'z', 'r', 't']:
                p[x] = row[x]
            keep.add(row['scn5a'])
        if remove_unlisted:
            print('Removing positions without NavAb equivalent')
            for k in set(position_properties.keys()) - keep:
                del(positions_properties[k])

    def _regions(self, connection, position_properties):
        """
        Adds region information to the position properties.

        Creates the following keys:

        regtype
            The type of region the position is in. Possible values are:
            'N-terminus', 'Segment 1', 'Segment 2', ..., 'Segment 6',
            'Linker 1-2', 'Linker 2-3', ..., 'Linker 5-6', 'Domain linker',
            and 'C-terminus'.
        segtype
            The type of segment the position is in. Possible values are:
            'Terminus', 'Segment', 'Linker' and 'Domain linker'.
        side
            The side of the membrane the position is on. Possible values are:
            'cytoplasmic', 'transmembrane' and 'extracellular'.

        """
        print('Loading region/segment/side data')
        c = connection.cursor()
        fields = ['regtype', 'segtype', 'side']
        for row in c.execute('select * from region'):
            for i in range(row['start'], 1 + row['end']):
                try:
                    p = position_properties[i]
                except KeyError:
                    continue
                for x in fields:
                    p[x] = row[x]

    def _gonnet_score(self, connection):
        """
        Returns a dict mapping an amino acid switch to a score. Each switch is
        encoded as a tuple of strings (old, new), where both strings are a
        one-letter amino acid code.
        """
        print('Loading Gonnet et al. scores')
        c = connection.cursor()
        score = {}
        for row in c.execute('select * from gonnet_score'):
            score[(row['key1'], row['key2'])] = row['score']
        return score

    def _grantham_score(self, connection):
        """
        Returns a dict mapping an amino acid switch to a score. Each switch is
        encoded as a tuple of strings (old, new), where both strings are a
        one-letter amino acid code.
        """
        print('Loading Grantham scores')
        c = connection.cursor()
        score = {}
        for row in c.execute('select * from grantham_score'):
            score[(row['key1'], row['key2'])] = row['score']
        return score

    def _segment_distance(self, connection, position_properties, name, where,
            add_squared=False):
        """
        Calculates the distance (as an amino acid count) to the nearest
        distance matching the 'where' part of the given query.

        For example `where='Segment 4'` calculates the distance to the nearest
        voltage sensor for every position.

        Adds it to position_properties under given the key `name`.

        If `add_squared` is True, the square of the distance will also be
        added, under the key `name + 'squared'`
        """
        print('Calculating amino acid count distances, where ' + where)
        c = connection.cursor()
        q = 'select * from region where ' + where
        # Fetch all SCN5A, isoform b positions. Need to refetch, because the
        # list in position_properties may be filtered.
        positions = self._positions(connection)
        indices = self._position_indices(connection)
        n = len(positions)
        # Calculate the smallest genetic distance to any of the segments
        # returned by the query
        distances = np.array([n**2]*n)
        for row in c.execute(q):
            # Get start and end indices in positions list
            start, end = indices[row['start']], indices[row['end']]+1
            # Set segment itself to zero
            distances[start:end] = 0
            # Update distances of previous positions
            distances[:start] = np.minimum(distances[:start],
                start-np.arange(start, dtype=int))
            # Update distance of next positions
            distances[end:] = np.minimum(distances[end:],
                1 + np.arange(0, n - end, dtype=int))
        # Add calculated distances to position properties
        for k, idx in enumerate(positions):
            try:
                p = position_properties[idx]
            except KeyError:
                continue
            p[name] = distances[k]
            if add_squared:
                p[name + 'squared'] = distances[k]**2
        # Debug
        if False:
            with open(name + '.txt', 'w') as f:
                ds = iter(distances)
                for k, idx in enumerate(positions):
                    f.write(str(idx) + ' ' + str(ds.next()) + '\n')

    def _region_types(self, connection):
        """
        Returns all existing region type strings.
        """
        c = connection.cursor()
        return [row['name'] for row in c.execute('select name from regtype')]

    def _segment_types(self, connection):
        """
        Returns all existing segment type strings.
        """
        c = connection.cursor()
        return [row['name'] for row in c.execute('select name from segtype')]

    def _side_types(self, connection):
        """
        Returns all existing side type strings.
        """
        c = connection.cursor()
        return [row['name'] for row in c.execute('select name from side')]

    def _acid_types(self, connection):
        """
        Returns all existing amino acid codes.
        """
        c = connection.cursor()
        return [row['name'] for row in c.execute('select name from acid')]

    def _zeroth_moment(self, connection, prop, radius, idx):
        """
        Calculates the zero-th order moment of size `n` for the acid property
        `property`, using the given `acid` at position `idx`.

        Arguments:

        ``connection``
            The connection to use.
        ``prop``
            The acid property to calculate the moment for.
        ``radius``
            The number of acids on either side of the selected acid that will
            be used
        ``idx``
            The position to calculate the moment for (i.e. a position label
            such as 1,558,1077 etc.).

        """
        c = connection.cursor()
        # Get scn5a isoform b residues
        residues = self._residues(connection)
        # Get index of position to look for
        indices = self._position_indices(connection)
        try:
            mid = indices[idx]
        except KeyError:
            raise KeyError('Position not found: ' + str(idx))
        # Get segment to use
        start = max(0, mid - radius)
        end = min(len(indices), mid + radius + 1)
        # Get acid properties
        acid_properties = self._acid_properties(connection)
        acid_properties = self._acid_properties(connection)
        # Calculate and return
        moment = 0
        for i in range(start, end):
            moment += acid_properties[residues[i]][prop]
        if False:
            positions = self._positions(connection)
            print([positions[x] for x in range(start, end)], moment)
        return moment

    def _position_properties(self, connection):
        """
        Creates a dict of properties for each position in SCN5A.
        """
        # Get positions
        positions = self._positions(connection)
        # Add properties
        position_properties = {}
        for p in positions:
            position_properties[p] = {}
        # Add NavAb spatial coordinates
        if False:
            self._navab_coordinates(connection, position_properties,
                remove_unlisted=True)
            positions = list(position_properties.keys())
            positions.sort()
        # Add conservedness scores
        self._conservedness(connection, position_properties,
            hse=True, dom=True)
        # Add regtype, segtype and side
        self._regions(connection, position_properties)
        # Add distance to voltage sensor
        self._segment_distance(connection, position_properties,
            'dseg4', 'regtype = "Segment 4"', add_squared=True)
        # Add distance to link voltage sensor and pore
        self._segment_distance(connection, position_properties,
            'dseg45', 'regtype = "Linker 4-5"', add_squared=True)
        # Add distance to pore-forming segment 5
        self._segment_distance(connection, position_properties,
            'dseg5', 'regtype = "Segment 5"', add_squared=True)
        # Add distance to pore-forming linker segments 5 and 6
        self._segment_distance(connection, position_properties,
            'dseg56', 'regtype = "Linker 5-6"', add_squared=True)
        # Add distance to pore-forming segment 6
        self._segment_distance(connection, position_properties,
            'dseg6', 'regtype = "Segment 6"', add_squared=True)
        # Distance to any transmembrane segment
        self._segment_distance(connection, position_properties,
            'dsegment', 'segtype like "Segment%"', add_squared=True)
        # Distance to D3-D4 linker, implicated in the inactivation process
        self._segment_distance(connection, position_properties,
            'dlink34', 'segment = "Linker D3-D4"', add_squared=True)
        # Distance to C-terminus, implicated in the inactivation process
        self._segment_distance(connection, position_properties,
            'dcterm', 'segment = "C-terminus"', add_squared=True)
        # Return
        return position_properties

    def create_discretized(self, connection, filename, dva=True, moments=False,
            acid_names=False, deltas_only=False, filtered=True):
        """
        Creates a CSV file with properties of mutations and a discretized
        dva or dvi output.

        Arguments:

        ``connection``
            A database connection to use.
        ``filename``
            The path/filename of the CSV file to create.
        ``dva``
            True to store DVA, False to store DVI.
        ``moments``
            Set to True to add zeroth moment properties.
        ``acid_names``
            Set to True to include the old/new acid names explicitly.
        ``deltas_only``
            Set to True to ignore old/new properties of amino acid.
        ``filtered``
            Set to True (default) to use the filtered epdata table.

        """
        # Get database cursor
        c = connection.cursor()

        # Load properties
        position_properties = self._position_properties(connection)
        acid_properties = self._acid_properties(connection)
        gonnet_score = self._gonnet_score(connection)
        grantham_score = self._grantham_score(connection)

        # Load mutations
        table = 'epdata_filtered' if filtered else 'epdata'
        fields = ['idx', 'old', 'new']
        fields += ['dva'] if dva else ['dvi']
        q = 'select desc,' + ','.join(fields) + ' from ' + table
        if dva:
            q += ' where dva is not null'
        else:
            q += ' where dvi is not null'
        mutations = []
        for row in c.execute(q):
            mutations.append([row[x] for x in fields])

        # Discretize voltage shifts
        print('Discretizing voltage shifts')
        discretization_names = [-1, 0,  1]
        discretization_bounds = [-2.5, 2.5]
        for mut in mutations:
            idx, old, new, dv = mut
            if dva:
                # Activation
                dva_disc = 0
                for upper in discretization_bounds:
                    if upper > dv:
                        break
                    dva_disc += 1
                mut[3] = discretization_names[dva_disc]
            else:
                # Inactivation
                dvi_disc = 0
                for upper in discretization_bounds:
                    if upper > dv:
                        break
                    dvi_disc += 1
                mut[3] = discretization_names[dvi_disc]

        # Create header for csv file
        header = []

        # Mutation properties
        header.append('index')
        if acid_names:
            header.append('old')
            header.append('new')

        # Amino acid properties
        if deltas_only:
            print('Only using amino acid DELTAs, no old or now')
            prefixes = ['delta']
        else:
            print('Using amino acid OLD, NEW and DELTAs')
            prefixes = ['old', 'new', 'delta']
        if moments:
            print('Using MOMENTS')
            prefixes += ['moment0r1', 'moment0r4', 'moment0r16']
        for x in prefixes:
            for y in self._acid_property_names():
                header.append(x + '_' + y)

        # Acid similarity scores
        header.append('gonnet')
        header.append('grantham')

        # Positional properties
        #header.append('dom')
        header.append('hse')
        header.append('regtype')
        header.append('segtype')
        header.append('side')
        header.append('dseg4')
        header.append('dseg45')
        header.append('dseg5')
        header.append('dseg56')
        header.append('dseg6')
        header.append('dsegment')
        header.append('dlink34')
        header.append('dcterm')

        # Physical locations
        if False:
            header.append('x')
            header.append('y')
            header.append('z')
            header.append('r')
            header.append('t')
            header.append('tmod')

        # Output
        if dva:
            print('Using ACTIVATION, discretized outputs')
            header.append('dva_disc')
        else:
            print('Using INACTIVATION, discretized outputs')
            header.append('dvi_disc')

        # Create data rows
        print('Creating mutation data')
        rows = []
        for idx, old, new, dv in mutations:
            #print(old + str(idx) + new)
            row = []
            # Add mutation data
            row.append(idx)
            if acid_names:
                row.append(old)
                row.append(new)
            # Add amino acid properties: old, new and delta
            properties = self._acid_property_names()
            p_old = [acid_properties[old][x] for x in properties]
            p_new = [acid_properties[new][x] for x in properties]
            if not deltas_only:
                for x in p_old:
                    row.append(x)
                for x in p_new:
                    row.append(x)
            for x in np.array(p_new) - np.array(p_old):
                row.append(x)
            if moments:
                radii = [1, 4, 16]
                for r in radii:
                    for p in properties:
                        row.append(self._zeroth_moment(connection, p, r, idx))
            # Add amino acid similarity scores
            row.append(gonnet_score[(old, new)])
            row.append(grantham_score[(old, new)])
            # Add positional properties
            properties = [
                #'dom',
                'hse',
                'regtype',
                'segtype',
                'side',
                'dseg4',
                'dseg45',
                'dseg5',
                'dseg56',
                'dseg6',
                'dsegment',
                'dlink34',
                'dcterm',
                ]
            for x in properties:
                row.append(position_properties[idx][x])
            # Add outcome
            row.append(dv)
            # Store row
            rows.append(row)

        # Write CSV file
        print('Writing CSV file.')
        with open(filename, 'w') as f:
            w = self.csv_writer(f)
            w.writerow(header)
            for row in rows:
                w.writerow(row)

    def create_class(self, connection, filename, output='act', moments=False,
            acid_names=False, deltas_only=False):
        """
        Creates a CSV file with properties of mutations and a single
        True/False output (act, inact, late, zero).

        Arguments:

        ``connection``
            A database connection to use.
        ``filename``
            The path/filename of the CSV file to create.
        ``output``
            The output to store (act, inact, late, zero, changed).
        ``moments``
            Set to True to add zeroth moment properties.
        ``acid_names``
            Set to True to include the old/new acid names explicitly.
        ``deltas_only``
            Set to True to ignore old/new properties of amino acid.

        """
        outputs = ['act', 'inact', 'late', 'zero']
        if output != 'changed' and output not in outputs:
            raise Exception('Output must be one of: ' + ', '.join(outputs)
                + ', or changed.')

        # Get database cursor
        c = connection.cursor()

        # Load properties
        position_properties = self._position_properties(connection)
        acid_properties = self._acid_properties(connection)
        gonnet_score = self._gonnet_score(connection)
        grantham_score = self._grantham_score(connection)

        # Create query to load mutations from db
        fields = ['idx', 'old', 'new'] + outputs
        q = 'select ' + ','.join(fields) + ' from epdata_outcomes'

        # Filter out rows for which the output is unknown
        if output not in ['zero', 'changed']:
            q += ' where ' + output + ' != 0'

        # Execute query, store mutations
        mutations = []
        for row in c.execute(q):
            d = {}
            for x in fields:
                d[x] = row[x]
            mutations.append(d)

        # Create header for CSV file
        header = []

        # Mutation properties
        header.append('index')
        if acid_names:
            header.append('old')
            header.append('new')

        # Amino acid properties
        if deltas_only:
            print('Only using amino acid DELTAs, no old or now')
            prefixes = ['delta']
        else:
            print('Using amino acid OLD, NEW and DELTAs')
            prefixes = ['old', 'new', 'delta']
        if moments:
            print('Using MOMENTS')
            prefixes += ['moment0r1', 'moment0r4', 'moment0r16']
        for x in prefixes:
            for y in self._acid_property_names():
                header.append(x + '_' + y)

        # Acid similarity scores
        header.append('gonnet')
        header.append('grantham')

        # Positional properties
        #header.append('dom')
        header.append('hse')
        header.append('regtype')
        header.append('segtype')
        header.append('side')
        header.append('dseg4')
        header.append('dseg45')
        header.append('dseg5')
        header.append('dseg56')
        header.append('dseg6')
        header.append('dsegment')
        header.append('dlink34')
        header.append('dcterm')

        # Physical locations
        if False:
            header.append('x')
            header.append('y')
            header.append('z')
            header.append('r')
            header.append('t')
            header.append('tmod')

        # Output
        print('Using output ' + output.upper())
        header.append(output)

        # Create data rows
        print('Creating mutation data')
        rows = []
        for mut in mutations:
            old, new, idx = mut['old'], mut['new'], mut['idx']
            row = []

            # Add mutation data
            row.append(idx)
            if acid_names:
                row.append(old)
                row.append(new)

            # Add amino acid properties: old, new and delta
            properties = self._acid_property_names()
            p_old = [acid_properties[old][x] for x in properties]
            p_new = [acid_properties[new][x] for x in properties]
            if not deltas_only:
                for x in p_old:
                    row.append(x)
                for x in p_new:
                    row.append(x)
            for x in np.array(p_new) - np.array(p_old):
                row.append(x)
            if moments:
                radii = [1, 4, 16]
                for r in radii:
                    for p in properties:
                        row.append(self._zeroth_moment(connection, p, r, idx))

            # Add amino acid similarity scores
            row.append(gonnet_score[(old, new)])
            row.append(grantham_score[(old, new)])

            # Add positional properties
            properties = [
                #'dom',
                'hse',
                'regtype',
                'segtype',
                'side',
                'dseg4',
                'dseg45',
                'dseg5',
                'dseg56',
                'dseg6',
                'dsegment',
                'dlink34',
                'dcterm',
                ]
            for x in properties:
                row.append(position_properties[idx][x])

            # Add outcome
            if output == 'changed':
                row.append(
                    mut['act'] > 0 or
                    mut['inact'] > 0 or
                    mut['late'] > 0 or
                    mut['zero'] > 0
                )
            else:
                row.append(mut[output] > 0)

            # Store row
            rows.append(row)

        # Write CSV file
        print('Writing CSV file.')
        with open(filename, 'w') as f:
            w = self.csv_writer(f)
            w.writerow(header)
            for row in rows:
                w.writerow(row)

    def _run(self):
        """
        Creates the csv files!
        """
        with base.connect() as connection:
            filename = self.data_out('dva-disc.csv')
            self.create_discretized(connection, filename,
                dva=True,
                moments=False,
                deltas_only=True,
                )
            filename = self.data_out('dvi-disc.csv')
            self.create_discretized(connection, filename,
                dva=False,
                moments=False,
                deltas_only=True,
                )
            filename = self.data_out('zero.csv')
            self.create_class(connection, filename, output='zero',
                deltas_only=True)
            filename = self.data_out('act.csv')
            self.create_class(connection, filename, output='act',
                deltas_only=True)
            filename = self.data_out('inact.csv')
            self.create_class(connection, filename, output='inact',
                deltas_only=True)
            filename = self.data_out('late.csv')
            self.create_class(connection, filename, output='late',
                deltas_only=True)


if __name__ == '__main__':
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
