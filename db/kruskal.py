#!/usr/bin/env python
#
# Kruskal-Wallis test example from:
#  Probability & Statistics for Engineers & Scientists
#  Walpole, Myers, Myers, ye
#  8th edition, 2007, Pearson
#
# Recreated in scipy
#
from __future__ import print_function, division
import numpy as np
import scipy
import scipy.stats

# Observations
groups = []
groups.append(np.array([
    24,
    16.7,
    22.8,
    19.8,
    18.9,
]))
groups.append(np.array([
    23.2,
    19.8,
    18.1,
    17.6,
    20.2,
    17.8,
]))
groups.append(np.array([
    18.4,
    19.1,
    17.3,
    17.3,
    19.7,
    18.9,
    18.8,
    19.3,
]))

# Get group sizes
ns = np.array([len(group) for group in groups])
print('Group sizes: ', ns)

# Get combined data
combined = np.concatenate(groups)
print('Len combined: ', len(combined))

# Get group split points
group_split_points = np.cumsum(ns)[:-1]


#
# Calculate ranks
#

# Get ordering of differences
isort = np.argsort(combined) # Sorts combined increasingly
rsort = np.argsort(isort)    # Inverse operation

# Sort combined data
combined = combined[isort]

# Create list of ranks (1, 2, 3, ...) to assign
n = len(combined)
ranks = np.array([i for i in range(1, 1 + n)], dtype=float)

# Average ranks where subsequent dmeans are the same
nsame = 0
for i in range(n - 1):
    if combined[i] == combined[i + 1]:
        nsame += 1
    elif nsame > 0:
        ranks[i - nsame:i + 1] = np.mean(ranks[i - nsame:i + 1])
        nsame = 0
if nsame > 0:
    ranks[-(1 + nsame):] = np.mean(ranks[-(1 + nsame):])

# Transform ranks back to ordering of dmu
ranks = ranks[rsort]

# Split back into groups
group_ranks = np.split(ranks, group_split_points)
print('Group ranks')
print(group_ranks)

#
# Compare groups
#
rs = np.array([np.sum(rank) for rank in group_ranks])
print('Group ri values')
print(rs)
n = len(combined)
h = np.sum(rs**2 / ns) * (12 / (n * (n + 1))) - 3 * (n + 1)
h_book = (12 / (19 * 20))
h_book *= 61**2 / 5 + 63.5**2 / 6 + 65.5**2 / 8
h_book -= 3 * 20
print('Statistic: h=' + str(h))
print('From book: h=' + str(h_book))
print('Using alpha=0.05, we get chi-squared is 5.991 for 2 degrees of freedom')
print('So h > 5.991 is false')
print('We _cannot_ reject the null hypothesis that the groups are from the same'
      ' distribution.')
print()

#
# Using scipy
#
print('Now using scipy')
print(scipy.stats.kruskal(*groups))
print('It seems they use a slightly different definition, but with almost the'
      ' same result!')
print('The given pvalue is the value for which we can reject the hypothesis'
      ' that the groups are the same.')
print('I.E., it\'s the value for which we can say the groups are different.')
print('If the pvalue is high, we cannot say the groups are different.')

