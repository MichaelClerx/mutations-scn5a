#!/usr/bin/env python
#
# Converts the matrix into a two-column csv file
#
# Read replacements
replacements = {}
filename = 'pam1_zero_diagonal.csv'
print('Reading ' + filename)
with open(filename, 'r') as f:
    # Read header
    header = f.next().strip().split(',')
    # Get order of amino acids
    order = header[1:]
    # Read
    for row in f:
        row = row.strip().split(',')
        replacement = row[0]
        i = iter(row[1:])
        for original in order:
            f = i.next()
            print(original + ' to ' + replacement + ' : ' + str(f))
            replacements[(original, replacement)] = f
# Write
filename = 'pam1_probabilities.csv'
print('Writing ' + filename)
with open(filename, 'w') as f:
    f.write('old, new, f\n')
    for old, new in sorted(replacements.keys()):
        f.write(old + ', ' + new + ', ' + replacements[(old, new)] + '\n')
print('Done.')
