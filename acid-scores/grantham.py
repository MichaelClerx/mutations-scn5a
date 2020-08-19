#!/usr/bin/env python
#
# Converts the Grantham matrix to a pair-wise score
#
# Read replacements
replacements = {}
filename = 'grantham.csv'
print('Reading ' + filename)
rows = []
arow = []
acol = []
with open(filename, 'r') as f:
    for k, line in enumerate(f):
        if k == 0:
            continue
        elif k > 22:
            break
        row = line.strip().split(',')
        if k == 1:
            acol = row[:-2]
        elif k < 21:
            arow.append(row[-2])
            row = row[k-2:-2]
            row = [float(x) for x in row]
            print(row)
            rows.append(row)

if arow[1:] != acol[:-1]:
    print('Warning: Order of acids in rows does not match order in columns')
    print(arow + [' '])
    print([' '] + acol)
# Write list of replacements
minscore = float('inf')
maxscore = -minscore
filename = 'grantham_score.csv'
print('Writing ' + filename)
with open(filename, 'w') as f:
    f.write('key1,key2,score\n')
    for i, ar in enumerate(arow):
        for j, ac in enumerate(acol[i:]):
            score = rows[i][j]
            f.write(ar + ',' + ac + ',' + str(score) + '\n')
            f.write(ac + ',' + ar + ',' + str(score) + '\n')
            minscore = min(score, minscore)
            maxscore = max(score, maxscore)
print('Lowest score : ' + str(minscore))
print('Highest score: ' + str(maxscore))
print('Done')
