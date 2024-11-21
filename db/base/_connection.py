#!/usr/bin/env python3
#
# Provides connections to the mutation database.
#
import base
import os
import csv
import sqlite3

# Tables (in order of creation)
FOR_SUPPLEMENT = False
_TABLES = [
    'bool',
    'tribool',
    'yesno',
    'cell_type',
    'scn5a_sequence',
    'transfection_type',
    'journal',
    'publication',
    'publication_tex',
    'midpoints_myo',
    'midpoints_wt',
]

# Table fields and restrictions
# Constraints must be given after all fields have been specified
_FIELDS = {
    # Bool (0=False, 1=True)
    'bool' : [
        'key int primary key not null',
        'desc text not null',
    ],
    # Tribool (-1=False, 0=Unknown, 1=True)
    'tribool' : [
        'key int primary key not null',
        'desc text not null',
    ],
    # Textual yes/no bool, or empty
    'yesno' : [
        'key text primary key not null',
    ],
    # All cell types used
    'cell_type' : [
        'key text not null',
        'description text not null',
        'PRIMARY KEY (key)',
    ],
    # All scn5a sequences measured
    # key: A unique identifier for this sequence
    # acc:
    'scn5a_sequence' : [
        'key text not null',
        'acc text',
        'description text not null',
        'PRIMARY KEY (key)',
    ],
    # Transfection type
    'transfection_type' : [
        'key text not null',
        'PRIMARY KEY (key)',
    ],
    # Journal: Each publication should link to a journal.
    'journal' : [
        'key text primary key not null',
        'name text not null',
        'translation text',
    ],
    # Publication: All EP data must come from some publication. Mutations are
    # not required to have a publication, but mutations can be associated with
    # multiple mutations in the `reports` table.
    'publication' : [
        'key text primary key not null',
        'author text not null',
        'year int not null',
        'journal text',
        'title text not null',
        'FOREIGN KEY (journal) REFERENCES journal(key)',
    ],
    # Tex references of publications
    'publication_tex': [
        'key text not null',
        'tex text not null',
        'PRIMARY KEY (key, tex)',
        'FOREIGN KEY (key) REFERENCES publication(key)',
    ],
    # WT Midpoints of activation and inactivation, measured in human atrial or
    # ventricular myocytes.
    'midpoints_myo' : [
        'pub text not null',
        'va float',
        'sema float',
        'na float',
        'stda float',
        'vi float',
        'semi float',
        'ni float',
        'stdi float',
        'sequence text',
        'key text',
        'celltype text',
        'celltype_full text',
        'beta1 text',
        'tmin float',
        'tmax float',
        'notes text',
        'FOREIGN KEY (pub) REFERENCES publication(key)',
    ],
    # WT Midpoints of activation and inactivation, measured in expression
    # systems.
    'midpoints_wt' : [
        'pub text not null',
        'va float not null',    # Mean midpoint of activation mV
        'sema float not null',  # SEM
        'na float not null',    # n for va
        'stda float not null',  # standard deviation calculated from SEM and n
        'vi float not null',    # Mean midpoint of inactivation mV
        'semi float not null',  # SEM
        'ni float not null',    # n for vi
        'stdi float not null',  # standard deviation calculated from SEM and n
        'ka float',             # Slope of activation boltzman (positive)
        'ki float',             # Slope of inactivation boltzman (negative)
        'sequence text',        # Code for sequence (a, a*, etc)
        'sequence_full text',   # Full sequence name given (hH1, M77235, etc)
        'cell text',            # Cell type, e.g. HEK, CHO
        'cell_full text',       # Cell type, e.g. HEK293, CHO-K1
        'beta1 text',           # Beta1 coexpressed yes/no
        'tmin float',           # Minimum temperature
        'tmax float',           # Maximum temperature
        'trtype text',          # Transfection type
        'trmin float',          # Min hours transfected
        'trmax float',          # Max hours transfected
        'ljp_corrected text',   # Yes/no/null
        'ljp float',            # LJP value
        'rpmin float',          # Minimum R pipette used/accepted MOhm
        'rpmax float',          # Maximum R pipette used/accepted MOhm
        'rsmin float',          # Minimum R series used/accepted MOhm
        'rsmax float',          # Maximum R series used/accepted MOhm
        'rscmin int',           # Min Rs compensation (0-100)
        'rscmax int',           # Max Rs compensation (0-100)
        'waitmin int',          # Min minutes waited after rupture
        'waitmax int',          # Max minutes waited after rupture
        'imin float',           # Minimum Ipeak accepted pA
        'imax float',           # Maximum Ipeak accepted pA
        'vpeak float',          # V eliciting peak current mV
        'ipeak float',          # Peak current pA
        'irep float',           # Peak current of "representative" trace pA
        't_cycle float',        # Seconds between sweeps
        'pah int',              # Holding potential, activation
        'palo int',             # Lowest tested, activation
        'pad int',              # Increment, activation
        'pahi int',             # Highest tested, activation
        'pih int',              # Holding potential, inactivation
        'pilo int',             # Lowest tested, inactivation
        'pid int',              # Increment, inactivation
        'pihi int',             # Highest tested, inactivation
        'pit int',              # Test potential, inactivation
        'boltz_ag yesno',       # Fit Boltzman to G for activation
        'boltz_ii yesno',       # Fit Boltzman to I for inactivation
        'na_e float',           # [Na]e mM
        'na_e2 float',          # [Na]e mM alternative
        'ca_e float',           # [Ca]e mM
        'tea_e float',          # Tetraethylammonium external mM (K-blocker)
        'nmdg_e float',         # NMDG external mM (Na replacement)
        'choline_e float',      # Choline external mM (Na replacement)
        'ph_e float',           # pH external
        'mix_e text',           # Substance used to correct external pH
        'bath text',            # Bath solution
        'na_i float',           # [Na]i mM
        'ca_i float',           # Ca added internally mM
        'mg_i float',           # Mg added internally mM
        'atp_i float',          # ATP internal mM (Mg and Ca buffer)
        'egta_i float',         # EGTA internal mM (Ca buffer)
        'bapta_i float',        # BAPTA internal mM (Ca buffer)
        'ca_ib float',          # [Ca]i calculated, with buffering
        'tea_i float',          # Tetraethylammonium internal mM (K-blocker)
        'ph_i float',           # pH internal
        'mix_i text',           # Substance used to correct internal pH
        'pipette text',         # Pipette solution
        'equipment text',       # Patch clamp hardware and software
        'notes text',
        'FOREIGN KEY (pub) REFERENCES publication(key)',
        'FOREIGN KEY (sequence) REFERENCES scn5a_sequence(key)',
        'FOREIGN KEY (cell) REFERENCES cell_type(key)',
        'FOREIGN KEY (beta1) REFERENCES yesno(key)',
        'FOREIGN KEY (trtype) REFERENCES transfection_type(key)',
        'FOREIGN KEY (ljp_corrected) REFERENCES yesno(key)',
    ],
}


def connect():
    """
    Connects to the database and returns the new :class:`Connection` object.
    """
    return Connection()


class Connection(object):
    """
    Context manager that maintains a connection to an sqlite database
    containing the mutation data from the ``csv`` files.
    """
    def __init__(self):
        super(Connection, self).__init__()
        self._filename = os.path.join(base.DIR_CACHE, base.FILE_CACHE)
        self._connection = None

    def _build_and_connect(self):
        """
        Builds or rebuilds the cache file from the source ``csv`` files and
        connects to it.
        """
        # Remove existing cache file
        if os.path.exists(self._filename):
            os.remove(self._filename)
        # Finished flag: Tidy up after this method if not set
        finished = False
        try:
            # Open new connection
            self._connect()
            # Get cursor and create tables
            c = self._connection.cursor()
            for table in _TABLES:
                print('Creating table `' + table + '`')
                # Create table
                f = '(' + ', '.join(_FIELDS[table]) + ')'
                q = 'CREATE TABLE ' + table + ' ' + f + ';'
                try:
                    c.execute(q)
                except sqlite3.Error as e:
                    print('*'*79)
                    print('Error executing statement:')
                    print(q)
                    print('*'*79)
                    raise
                # Add data
                path = os.path.join(base.DIR_DATA_IN, table + '.csv')
                with open(path, 'r') as f:
                    # Create csv reader
                    reader = csv.reader(f, **base.CSV_OPTIONS)
                    # Get fields required by table specification
                    fields = _FIELDS[table]
                    # Gather field names
                    fnames = []
                    # Check file header
                    header = next(reader)
                    for k, field in enumerate(header):
                        required = (fields[k].split(' '))[0]
                        if field != required:
                            raise Exception('Field mismatch in `' + table
                                + '` in column (' + str(1 + k)
                                + '), expected "' + required + '" got "'
                                + field + '".')
                        fnames.append(field)
                    print('Table header ok!')
                    # Create insertion query
                    q = 'INSERT INTO `' + table + '`'
                    q += ' (' + ', '.join(fnames) + ')'
                    q += ' VALUES (' + ', '.join(['?']*len(fnames)) + ');'
                    try:
                        for row in reader:
                            # Skip empty rows
                            if not row:
                                continue
                            data = []
                            for x in row:
                                if x == 'None':
                                    data.append(None)
                                else:
                                    #data.append(bytes(x, 'utf8'))
                                    data.append(str(x))
                            c.execute(q, data)
                    except sqlite3.Error as e:
                        print('*'*79)
                        print('Error executing statement:')
                        print(q)
                        print(row)
                        print('*'*79)
                        raise
            # Commit!
            self._connection.commit()
            # Done! Set finished flag to True
            finished = True
        finally:
            if not finished:
                # Not finished? Then close connection...
                if self._connection:
                    self._connection.close()
                    self._connection = None
                # ...and delete created file.
                if os.path.exists(self._filename):
                    os.remove(self._filename)

    def _connect(self):
        """
        Connects to a new or existing cache file.
        """
        # Test if connection is already set up
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            raise Exception('Connection already open when entering!')
        # Set up connection
        self._connection = sqlite3.connect(self._filename)
        # Enable foreign keys
        c = self._connection.cursor()
        c.execute('PRAGMA foreign_keys = ON;')
        self._connection.commit()
        # Set row factory (to enable name based access)
        self._connection.row_factory = sqlite3.Row

    def __enter__(self):
        """
        Called when the context manager is entered. Opens a connection to a new
        or cached sqlite database containing the data from the ``csv`` files.
        """
        # Cache update needed?
        if self._need_build():
            # Create new cache file and connect to it
            self._build_and_connect()
        else:
            # Set up connection to cached file and return
            self._connect()
        return self._connection

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called when the context manager is exited. Closes the connection.
        """
        if self._connection:
            self._connection.close()
            self._connection = None

    def _need_build(self):
        """
        Checks if the cache file exists and is up to date. Returns ``True`` if
        the cache needs to be generated.
        """
        # Check if the cache file exists
        if not os.path.exists(self._filename):
            return True
        # Check if the cache is actually a file
        if not os.path.isfile(self._filename):
            return True
        # Get the earliest date associated with this file
        cache_time = min(
            os.path.getmtime(self._filename),
            os.path.getatime(self._filename))
        # Check if any of the csv files are newer
        for table in _TABLES:
            # Check for table input file
            path = os.path.join(base.DIR_DATA_IN, table + '.csv')
            if not os.path.isfile(path):
                raise Exception('Missing input file: ' + path)
            # Get the latest date this file was modified (or touched)
            time = max(os.path.getmtime(path), os.path.getatime(path))
            # Invalidate cache if required
            if time > cache_time:
                return True
        return False
