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
    'journal',
    'publication',
    'charge',
    'acid',
    'gonnet_score',
    'grantham_score',
    'cell_type',
    'scn5a',
    'scn5a_isoform_b',
    'scn5a_sequence',
    'segtype',
    'regtype',
    'side',
    'domain',
    'region',
    'conservedness',
    'mutation',
    'mutation_possible',
    'report',
    'epdata',
    'epdata_filtered',
    ]
if not FOR_SUPPLEMENT:
    _TABLES += [
        'scn9a',
        'midpoints_wt',
        'midpoints_myo',
        'clinical',
        'navab_to_scn5a',
        'navab_locations',
        'scn5a_dimos_locations',
        'scn5a_dimos_locations_interpolated',
        'scn5a_navab_locations_interpolated',
        'scn5a_diagram',
        'pam1_probabilities',
        'publication_tex',
        ]
# Table fields and restrictions
# Constraints must be given after all fields have been specified
_FIELDS = {
    #
    # Bool (0=False, 1=True)
    #
    'bool' : [
        'key int primary key not null',
        'desc text not null',
        ],
    #
    # Tribool (-1=False, 0=Unknown, 1=True)
    #
    'tribool' : [
        'key int primary key not null',
        'desc text not null',
        ],
    #
    # Bool (yes/no) or tribool (yes/no/null)
    #
    'yesno' : [
        'key text primary key not null',
        ],
    #
    # Journal: Each publication should link to a journal.
    #
    'journal' : [
        'key text primary key not null',
        'name text not null',
        'translation text',
        ],
    #
    # Publication: All EP data must come from some publication. Mutations are
    # not required to have a publication, but mutations can be associated with
    # multiple mutations in the `reports` table.
    #
    'publication' : [
        'key text primary key not null',
        'author text not null',
        'year int not null',
        'journal text',
        'title text not null',
        'FOREIGN KEY (journal) REFERENCES journal(key)',
        ],
    #
    # Tex references of publications
    #
    'publication_tex': [
        'key text not null',
        'tex text not null',
        'PRIMARY KEY (key, tex)',
        'FOREIGN KEY (key) REFERENCES publication(key)',
        ],
    #
    # Values for the enum field `charge` (positive, negative, zero)
    #
    'charge' : [
        'key int primary key not null',
        ],
    #
    # Amino acid properties. Each acid is identified by a one letter code. In
    # addition, they have a 3 letter code and a full name.
    #
    # Properties:
    #   - Average residue mass (float)
    #   - Percent buried residues (float)
    #   - Van-der-waals volume (float)
    #   - Polarity ranking (float)
    #   - Charge (a value from the 'charge' table)
    #   - Hydrophobicity, according to Kovacs et al. (float)
    #   - Helix propensity, according to Pace et al. (float)
    #
    'acid' : [
        'key text primary key not null',
        'key3 text unique not null',
        'name text unique not null',
        'average_residue_mass float',
        'percent_buried_residues float',
        'v_waals float',
        'polarity_ranking float',
        'charge int not null',
        'hydrophobicity float',
        'helix_propensity float',
        'FOREIGN KEY (charge) REFERENCES charge(key)',
        ],
    #
    # Amino acid conservation score according to: Gonnet, Cohen, Benner
    # Exhaustive matching of the entire protein sequence database
    # Science, 1992
    #
    'gonnet_score' : [
        'key1 text not null',
        'key2 text not null',
        'score float not null',
        'PRIMARY KEY (key1, key2)',
        'FOREIGN KEY (key1) REFERENCES acid(key)',
        'FOREIGN KEY (key2) REFERENCES acid(key)',
        ],
    #
    # Amino acid similarity according to: Grantham
    # Amino Acid Difference Formula to Help Explain Protein Evolution
    # Science, 1974
    #
    'grantham_score' : [
        'key1 text not null',
        'key2 text not null',
        'score int not null',
        'PRIMARY KEY (key1, key2)',
        'FOREIGN KEY (key1) REFERENCES acid(key)',
        'FOREIGN KEY (key2) REFERENCES acid(key)',
        ],
    #
    # All positions (which are labels!) in SCN5A, isoform a. Ordered.
    #
    'scn5a' : [
        'idx int primary key not null',
        'acid text not null',
        'FOREIGN KEY (acid) REFERENCES acid(key)',
        'UNIQUE (idx, acid)',
        ],
    #
    # All positions (which are labels!) in SCN5A, isoform b. Ordered.
    #
    'scn5a_isoform_b' : [
        'idx int primary key not null',
        'acid text not null',
        'FOREIGN KEY (acid) REFERENCES acid(key)',
        'UNIQUE (idx, acid)',
        ],
    #
    # All positions (which are labels!) in SCN9A. Ordered.
    #
    'scn9a' : [
        'idx int primary key not null',
        'acid text not null',
        'FOREIGN KEY (acid) REFERENCES acid(key)',
        'UNIQUE (idx, acid)',
        ],
    #
    # Types of segment (Terminus, Segment, Linker, Domain linker)
    #
    'segtype' : [
        'name text primary key not null',
        ],
    #
    # Types of region (N-terminus, Segment 1,2,.., Linker 1-2, 2-3,...,
    # Domain Linker, C-terminus).
    #
    'regtype' : [
        'name text primary key not null',
        ],
    #
    # Side of the membrane (cytoplasmic, transmembrane, extracellular)
    #
    'side' : [
        'name text primary key not null',
        ],
    #
    # Side of the membrane (cytoplasmic, transmembrane, extracellular)
    #
    'domain' : [
        'name text primary key not null',
        ],
    #
    # Regions of SCN5A isoform b, along with information about each region.
    # Regions are encoded using a start and an _inclusive_ finish.
    #
    'region' : [
        'name text primary key not null',
        'domain text not null',
        'segment text not null',
        'segtype text not null',
        'regtype text not null',
        'side text not null',
        'start int not null',
        'end int not null',
        'length int not null',
        'FOREIGN KEY (start) REFERENCES scn5a(idx)',
        'FOREIGN KEY (end) REFERENCES scn5a(idx)',
        'FOREIGN KEY (domain) REFERENCES domain(name)',
        'FOREIGN KEY (segtype) REFERENCES segtype(name)',
        'FOREIGN KEY (regtype) REFERENCES regtype(name)',
        'FOREIGN KEY (side) REFERENCES side(name)',
        'CHECK (end > start)',
        'CHECK (end - start + 1 == length)',
        ],
    #
    # Conservation scores for each position in SCN5A isoform a, according to
    # different measures.
    #
    # hse: Human-Squid-Eel index, calculated by me by aligning all human SCNxA
    #      isoforms, along with a squid and an eel channel.
    # dom: Domain index, calculated by me by aligning the four domains.
    #
    'conservedness' : [
        'idx int primary key not null',
        'hse int not null',
        'dom int not null',
        'FOREIGN KEY (idx) REFERENCES scn5a(idx)',
        ],
    #
    # All cell types used
    #
    #
    'cell_type' : [
        'key text not null',
        'description text not null',
        'PRIMARY KEY (key)',
        ],
    #
    # All scn5a sequences measured
    #
    # key: A unique identifier for this sequ
    # acc:
    #
    'scn5a_sequence' : [
        'key text not null',
        'acc text',
        'description text not null',
        'PRIMARY KEY (key)',
        ],
    #
    # All mutations: natural, artifical, investigated, important, unimportant,
    # with epdata, without epdata etc.
    #
    'mutation' : [
        'old text not null',
        'idx int not null',
        'new text not null',
        'PRIMARY KEY (old, idx, new)',
        'FOREIGN KEY (old) REFERENCES acid(key)',
        'FOREIGN KEY (new) REFERENCES acid(key)',
        'FOREIGN KEY (old, idx) REFERENCES scn5a(acid, idx)',
        ],
    #
    # All possible missense mutations resulting from a single nucleotide
    # exchange in SCN5A (isoform a).
    #
    'mutation_possible' : [
        'old text not null',
        'idx int not null',
        'new text not null',
        'weight float not null',
        'simple_weight float not null',
        'PRIMARY KEY (old, idx, new)',
        'FOREIGN KEY (old) REFERENCES acid(key)',
        'FOREIGN KEY (new) REFERENCES acid(key)',
        'FOREIGN KEY (old, idx) REFERENCES scn5a(acid, idx)',
        ],
    #
    # Any link between a publication and a mutation, should exist whenever a
    # publication contains new experimental data (epdata or population data)
    # about a mutation.
    # Obviously not complete.
    #
    'report' : [
        'old text not null',
        'idx int not null',
        'new text not null',
        'pub text not null',
        'PRIMARY KEY (old, idx, new, pub)',
        'FOREIGN KEY (old, idx, new) REFERENCES mutation(old, idx, new)',
        'FOREIGN KEY (pub) REFERENCES publication(key)',
        ],
    #
    # Cellular electrophysiology data reported for mutations.
    # Each entry contains information from one publication about one mutation.
    # Publications can have multiple entries about the same mutation.
    # All measurements must be made in a homozygous context.
    #
    # Fields:
    #
    # key
    #   An auto-incrementing key.
    # old
    #   The original residue.
    # idx
    #   The mutation's position (as a label)
    # new
    #   The replacement residue.
    # pub
    #   The publication that this ep data is from.
    # desc
    #   An optional, unformatted textual description
    # dva
    #   The (significant or insignificant) shift in midpoint of activation.
    #   A 0 indicates the shift was measured and found to be exactly 0, or not
    #   large enough to mention.
    #   A `None` means it wasn't measured or that no numerical values was
    #   reported.
    # dvi
    #   The (significant or insignificant) shift in midpoint of inactivation.
    #   A 0 indicates the shift was measured and found to be exactly 0, or not
    #   large enough to mention.
    #   A `None` means it wasn't measured or that no numerical values was
    #   reported.
    # zero (bool)
    #   True if expressing this mutant didn't lead to an appreciable current.
    #   A 1 indicates the mutant was expressed but no current could be recorded
    #   A 0 indicates it was found the mutated channel does produce a
    #   measurable current.
    # act (tribool)
    #   True if there was any significant change in activation (midpoint,
    #   timing or whatever)
    #   A 1 indicates a significant change was seen. A -1 indicates activation
    #   was tested (somehow) but found to be unchanged. A 0 indicates nobody
    #   checked (directly) in any way.
    # inact (tribool)
    #   True if there was any significant change in inactivation (midpoint,
    #   timing, recovery or whatever)
    #   A 1 indicates a significant change was seen. A -1 indicates activation
    #   was tested (somehow) but found to be unchanged. A 0 indicates nobody
    #   checked (directly) in any way.
    # late (tribool)
    #   True if there was any significant change in the late sodium current.
    #   A 1 indicates a significant change was seen. A -1 indicates activation
    #   was tested (somehow) but found to be unchanged. A 0 indicates nobody
    #   checked (directly) in any way.
    # sequence
    #   The sequence id of the alpha subunit used in testing
    # sequence_full
    #   The alpha subunit used, as given in the text
    # cell
    #   The cell type id used in testing
    # cell_full
    #   The cell type as given in the text
    # beta1 (yes/no)
    #   Yes if a beta1 subunit was co-expressed
    # notes (text)
    #   A textual field for notes about the data
    #
    'epdata' : [
        'key integer primary key',
        'old text not null',
        'idx int not null',
        'new text not null',
        'pub text not null',
        'desc text',
        'dva float',
        'dvi float',
        'zero int not null',
        'act int not null',
        'inact int not null',
        'late int not null',
        'sequence text',
        'sequence_full text',
        'cell text',
        'cell_full text',
        'beta1 text',
        'notes text',
        'FOREIGN KEY (old, idx, new, pub) REFERENCES report(old, idx, new, pub)',
        'FOREIGN KEY (sequence) REFERENCES scn5a_sequence(key)',
        'FOREIGN KEY (cell) REFERENCES cell_type(key)',
        'FOREIGN KEY (zero) REFERENCES bool(key)',
        'FOREIGN KEY (act) REFERENCES tribool(key)',
        'FOREIGN KEY (inact) REFERENCES tribool(key)',
        'FOREIGN KEY (late) REFERENCES tribool(key)',
        'FOREIGN KEY (beta1) REFERENCES yesno(key)',
        ],
    #
    # Filtered version of `epdata`, used for machine learning.
    #
    #
    'epdata_filtered' : [
        'key integer primary key',
        'old text not null',
        'idx int not null',
        'new text not null',
        'pub text not null',
        'desc text',
        'dva float',
        'dvi float',
        'zero int not null',
        'act int not null',
        'inact int not null',
        'late int not null',
        'sequence text',
        'sequence_full text',
        'cell text',
        'cell_full text',
        'beta1 text',
        'notes text',
        'FOREIGN KEY (old, idx, new, pub) REFERENCES report(old, idx, new, pub)',
        'FOREIGN KEY (sequence) REFERENCES scn5a_sequence(key)',
        'FOREIGN KEY (cell) REFERENCES cell_type(key)',
        'FOREIGN KEY (zero) REFERENCES bool(key)',
        'FOREIGN KEY (act) REFERENCES tribool(key)',
        'FOREIGN KEY (inact) REFERENCES tribool(key)',
        'FOREIGN KEY (late) REFERENCES tribool(key)',
        'FOREIGN KEY (beta1) REFERENCES yesno(key)',
        ],
    #
    # WT Midpoints of activation and inactivation, measured in expression
    # systems.
    #
    'midpoints_wt' : [
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
        'sequence_full text',
        'cell text',
        'cell_full text',
        'beta1 text',
        'tmin float',
        'tmax float',
        'notes text',
        'FOREIGN KEY (pub) REFERENCES publication(key)',
        'FOREIGN KEY (sequence) REFERENCES scn5a_sequence(key)',
        'FOREIGN KEY (cell) REFERENCES cell_type(key)',
        'FOREIGN KEY (beta1) REFERENCES yesno(key)',
        ],
    #
    # WT Midpoints of activation and inactivation, measured in human atrial or
    # ventricular myocytes.
    #
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
    #
    # Clinical phenotype of mutations
    #TODO NOT FILLED IN YET
    #
    'clinical' : [
        'key integer primary key',
        'old text not null',
        'idx int not null',
        'new text not null',
        'pub text not null',
        'brs int not null',
        ],
    #
    # Alignment of NavAb with SCN5A, isoform b.
    # Each entry links a position label in NavAb to one in SCN5A
    #
    'navab_to_scn5a' : [
        'navab text primary key',
        'scn5a integer not null',
        ],
    #
    # Physical locations in three dimensions of NavAb amino acids.
    #
    'navab_locations' : [
        'key text primary key',
        'idx integer',
        'acid text not null',
        'x float',
        'y float',
        'z float',
        'r float',
        't float',
        'FOREIGN KEY (acid) REFERENCES acid(key)',
        ],
    #
    # Physical locations of SCN5A acids, based on the NavAb mapping, but with
    # a very simple linear interpolation for missing values. Really quite
    # wrong for linkers.
    #
    'scn5a_navab_locations_interpolated' : [
        'idx integer primary key',
        'x float',
        'y float',
        'z float',
        'r float',
        't float',
        ],
    #
    # Physical locations of a number of SCN5A acids, based on Dimos' model.
    #
    'scn5a_dimos_locations' : [
        'idx integer',
        'x float',
        'y float',
        'z float',
        'r float',
        't float',
        ],
    #
    # Physical locations of SCN5A acids, based on Dimos' model, but with a very
    # simple linear interpolation for missing values. Really quite wrong for
    # linkers.
    #
    'scn5a_dimos_locations_interpolated' : [
        'idx integer',
        'x float',
        'y float',
        'z float',
        'r float',
        't float',
        ],
    #
    # Diagrammatic, 2d locations of all acids in SCN5A, isoform a
    #
    'scn5a_diagram' : [
        'idx integer primary key',
        'x float',
        'y float',
        'FOREIGN KEY (idx) REFERENCES scn5a(idx)',
        ],
    #
    # Mutation probabilitymatrix, multiplied by 10000 and with the diagonal
    # set to zero. Based on chapter 22 in Dayhoff et al.'s atlas of protein
    # sequence and structure.
    #
    'pam1_probabilities' : [
        'old text not null',
        'new text not null',
        'f float',
        'PRIMARY KEY (old, new)'
        'FOREIGN KEY (old) REFERENCES acid(key)',
        'FOREIGN KEY (new) REFERENCES acid(key)',
        ],
    }
_INCREMENT = [
    'epdata',
    'epdata_filtered',
    'clinical',
    ]
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
                    offset = 1 if table in _INCREMENT else 0
                    for k, field in enumerate(header):
                        required = (fields[offset+k].split(' '))[0]
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
            #
            # Create annotated scn5a view
            #
            q = """
                CREATE VIEW scn5a_annotated AS
                    SELECT
                        s.*,
                        region.name as region,
                        region.domain,
                        region.regtype,
                        region.segment
                    FROM (
                        SELECT scn5a.*, hse as hse_score, dom as dom_score
                            FROM scn5a
                                LEFT JOIN conservedness
                                ON scn5a.idx == conservedness.idx
                        ) AS s
                        CROSS JOIN region
                    WHERE idx >= start AND idx <= "end" GROUP BY idx;
                """
            try:
                c.execute(q)
            except sqlite3.Error as e:
                print('Error creating view:')
                print(q)
                raise e
            #
            # Create annotated mutation view
            #
            q = """
                CREATE VIEW mutation_annotated AS
                    SELECT
                        mutation.*,
                        scn5a_annotated.region,
                        scn5a_annotated.domain,
                        scn5a_annotated.regtype,
                        scn5a_annotated.segment
                    FROM mutation
                    JOIN scn5a_annotated
                    ON mutation.idx = scn5a_annotated.idx;
                """
            try:
                c.execute(q)
            except sqlite3.Error as e:
                print('Error creating view:')
                print(q)
                raise e
            #
            # Create view of mutations, not including those only found in exac
            #
            q = """
                CREATE VIEW mutation_no_exac AS
                    SELECT distinct idx, old, new
                    FROM report
                    WHERE pub != "exac";
                """
            try:
                c.execute(q)
            except sqlite3.Error as e:
                print('Error creating view:')
                print(q)
                raise e
            #
            # Create annotated mutations-without-exac view
            #
            q = """
                CREATE VIEW mutation_no_exac_annotated AS
                    SELECT
                        mutation_no_exac.*,
                        scn5a_annotated.region,
                        scn5a_annotated.domain,
                        scn5a_annotated.regtype,
                        scn5a_annotated.segment
                    FROM mutation_no_exac
                    JOIN scn5a_annotated
                    ON mutation_no_exac.idx = scn5a_annotated.idx;
                """
            try:
                c.execute(q)
            except sqlite3.Error as e:
                print('Error creating view:')
                print(q)
                raise e
            #
            # Create annotated epdata view
            #
            q = """
                CREATE VIEW epdata_annotated AS
                    SELECT
                        epdata.*,
                        scn5a_annotated.region,
                        scn5a_annotated.domain,
                        scn5a_annotated.regtype,
                        scn5a_annotated.segment
                    FROM epdata
                    JOIN scn5a_annotated
                    ON epdata.idx = scn5a_annotated.idx;
                """
            try:
                c.execute(q)
            except sqlite3.Error as e:
                print('Error creating view:')
                print(q)
                raise e
            #
            # Create annotated epdata view with unique mutations and outcomes
            #
            # Shows the sum-of-votes score for 4 outcomes
            # An additional field shows whether positive and negative votes
            #  were balanced (for sum-of-votes == 0 fields)
            #
            q = """
                CREATE VIEW epdata_outcomes AS
                    SELECT old, idx, new, sum(act) as act, sum(inact) as inact,
                        sum(zero) as zero, sum(late) as late,
                        (sum(act == 1) > 0 and sum(act) == 0) as act_balanced,
                        (sum(inact == 1) > 0 and sum(inact) == 0) as inact_balanced,
                        (sum(zero == 1) > 0 and sum(zero) == 0) as zero_balanced,
                        (sum(late == 1) > 0 and sum(late) == 0) as late_balanced
                    FROM epdata
                    GROUP BY idx, new
                """
                # The final (sum(act ==...) stuff is to see how often we had
                # a tie and couldn't include data
            try:
                c.execute(q)
            except sqlite3.Error as e:
                print('Error creating view:')
                print(q)
                raise e

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
