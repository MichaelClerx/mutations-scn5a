#!/usr/bin/env python
#
# Converts the Gonnet matrix to a pair-wise score
#
# Read replacements
replacements = {}
filename = 'gonnet.csv'
print('Reading ' + filename)
rows = []
arow = []
acol = []
with open(filename, 'r') as f:
    for k, line in enumerate(f):
        row = line.strip().split(',')
        if k < 19:
            row = row[:row.index('')]
        if k < 20:
            arow.append(row[0])
            rows.append([float(x) for x in row[1:]])
        else:
            acol = row[1:]
            break
if arow != acol:
    print('Warning: Order of acids in rows does not match order in columns')
# Write list of replacements
minscore = float('inf')
maxscore = -minscore
filename = 'gonnet_score.csv'
print('Writing ' + filename)
with open(filename, 'w') as f:
    f.write('key1,key2,score\n')
    for i, ar in enumerate(arow):
        for j, ac in enumerate(acol):
            if ar == ac:
                break
            score = rows[i][j]
            f.write(ar + ',' + ac + ',' + str(score) + '\n')
            f.write(ac + ',' + ar + ',' + str(score) + '\n')
            minscore = min(score, minscore)
            maxscore = max(score, maxscore)
print('Lowest score : ' + str(minscore))
print('Highest score: ' + str(maxscore))
print('Done')
