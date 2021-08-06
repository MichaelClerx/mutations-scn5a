#!/usr/bin/env python3
#
# Attribute-Relation File Format (ARFF) class
#
#
#
import numbers
STRING = 0
NUMERIC = 1
NOMINAL = 2
class ARFFFile(object):
    """
    Represents a file in the Attribute-Relation File Format (ARFF).
    
    To create an ARFF file, first create an ARFFFile object, then add all the
    fields you need, then add rows of data. Once data has been added the fields
    remain fixed.
    
    Example::
    
        import arff
        a = arff.ARFFFile()
        a.add_field('
    
    """
    def __init__(self, relation):
        super(ARFFFile, self).__init__()
        # The name of the relation this ARRFFile describes
        self._relation = self._string(relation)
        if self._relation == '':
            raise ValueError('The relation name cannot be an empty string.')
        # This arff's field names
        self._names = []
        # This arff's field types
        self._types = []
        # Nominal data
        self._nominal = {}
        # This arff's data records
        self._data = []
        # A comment to display at the top of the file.
        self._comment = None
    def add_nominal_field(self, name, options):
        """
        Adds a nominal field ``name`` with the options specified in sequence
        ``options``.
        """
        name = self._name(name)
        options = [self._string(x) for x in options]
        if len(set(options)) < len(options):
            raise ValueError('Options for nominal field contains duplicates.')
        self._names.append(name)
        self._types.append(NOMINAL)
        self._nominal[name] = options
    def add_numeric_field(self, name):
        """
        Adds a numeric field to this file, using the given ``name``.
        """
        self._names.append(self._name(name))
        self._types.append(NUMERIC)
    def add_row(self, *args):
        """
        Adds a row of data to this file.
        """
        n = len(self._names)
        if len(args) != n:
            raise ValueError('Invalid row specification: Must contain exactly'
                ' (' + str(n) + ' values, got (' + str(len(args)) + ').')
        row = [None] * n
        for k, data in enumerate(args):
            datatype = self._types[k]
            if datatype == STRING:
                row[k] = self._string(data)
            elif datatype == NUMERIC:
                if not isinstance(data, numbers.Number):
                    raise ValueError('Invalid numeric data for attribute <'
                        + self._names[k] + '>: ' + str(data))
                row[k] = str(data)
            elif datatype == NOMINAL:
                choice = self._string(data)
                if choice not in self._nominal[self._names[k]]:
                    raise ValueError('Invalid option <' + choice
                        +'> for attribute <' + self._names[k]
                        + '>, must choose one of <'
                        + ','.join(self._nominal[self._names[k]]) + '>.')
                row[k] = choice
            else:
                raise Exception('Unhandled data type.')
        self._data.append(row)
    def add_string_field(self, name):
        """
        Adds a string field to this file, using the given ``name``.
        """
        self._names.append(self._name(name))
        self._types.append(STRING)
    def _name(self, name):
        """
        Pre-processes the given name and checks if it can be used as the name
        for a new field in the file.
        """
        if self._data:
            raise ValueError('Cannot add fields once data has been added.')
        name = self._string(name)
        if name == '':
            raise ValueError('Name cannot be empty string.')
        if name in self._names:
            raise ValueError('Name <' + name + '> already in use.')
        return name
    def set_comment(self, text):
        """
        Sets a comment to include at the top of this arff file.
        """
        self._comment = str(text)
    def _string(self, text):
        """
        Processes any string argument (names etc.) adding quotes if needed.
        """
        text = str(text)
        if ' ' in text or '"' in text:
            text = '"' + text.replace('"', '\\"')  + '"'
        return text
    def write(self, filename):
        """
        Writes this ARFFFile to disk.
        """
        with open(filename, 'w') as f:
            # 1. Comment
            if self._comment:
                f.write('%\n')
                for line in self._comment.splitlines():
                    f.write('% ' + line + '\n')
                f.write('%\n')
            # 2. Relation name
            f.write('@RELATION ')
            f.write(self._relation)
            f.write('\n\n')
            # 3. Attributes
            nspaces = 1 + max([len(name) for name in self._names])
            for k, name in enumerate(self._names):
                f.write('@ATTRIBUTE ')
                f.write(name)
                f.write(' ' * (nspaces - len(name)))
                datatype = self._types[k]
                if datatype == STRING:
                    f.write('STRING')
                elif datatype == NUMERIC:
                    f.write('NUMERIC')
                elif datatype == NOMINAL:
                    f.write('{')
                    f.write(','.join(self._nominal[name]))
                    f.write('}')
                else:
                    raise Exception('Unexpected data type' + str(datatype))
                f.write('\n')
            f.write('\n')
            # 4. Data
            f.write('@DATA\n')
            for row in self._data:
                f.write(','.join(row))
                f.write('\n')
#
# Simple test script
#       
if __name__ == '__main__':
    a = ARFFFile('test')
    a.add_string_field('name')
    a.add_numeric_field('age')
    a.add_nominal_field('gender', ['boy', 'girl'])
    a.add_row('Michael', 32, 'boy')
    a.add_row('Jennifer', 31, 'girl')
    a.set_comment('This is a very stupid test file\nWith silly information.')
    a.write('test.arff')
    
