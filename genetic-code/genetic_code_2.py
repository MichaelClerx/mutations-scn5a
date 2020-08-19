#!/usr/bin/env python3
#
# Genetic code
#
# The genetic code maps the space of RNA nucleotide triplets onto the extended
# amino acid space (20 acids plus a stop codon, the first M encountered serves
# as the start codon).
#
#
import sys

#
# All possible nucleotides, using `ucag' as the RNA sequence
#
nucleotides = set('ucag')
assert(len(nucleotides) == 4)

#
# All 20 common amino acids, plus 'x' for any stop codon
#
acids = set('arndceqghilkmfpstwyvx')
assert(len(acids) == 21)

#
# The genetic code (again using RNA nucleotides)
#
genmap = {
    'uuu' : 'f',
    'uuc' : 'f',
    'uua' : 'l',
    'uug' : 'l',

    'ucu' : 's',
    'ucc' : 's',
    'uca' : 's',
    'ucg' : 's',

    'uau' : 'y',
    'uac' : 'y',
    'uaa' : 'x',
    'uag' : 'x',

    'ugu' : 'c',
    'ugc' : 'c',
    'uga' : 'x',
    'ugg' : 'w',

    'cuu' : 'l',
    'cuc' : 'l',
    'cua' : 'l',
    'cug' : 'l',

    'ccu' : 'p',
    'ccc' : 'p',
    'cca' : 'p',
    'ccg' : 'p',

    'cau' : 'h',
    'cac' : 'h',
    'caa' : 'q',
    'cag' : 'q',

    'cgu' : 'r',
    'cgc' : 'r',
    'cga' : 'r',
    'cgg' : 'r',

    'auu' : 'i',
    'auc' : 'i',
    'aua' : 'i',
    'aug' : 'm',

    'acu' : 't',
    'acc' : 't',
    'aca' : 't',
    'acg' : 't',

    'aau' : 'n',
    'aac' : 'n',
    'aaa' : 'k',
    'aag' : 'k',

    'agu' : 's',
    'agc' : 's',
    'aga' : 'r',
    'agg' : 'r',

    'guu' : 'v',
    'guc' : 'v',
    'gua' : 'v',
    'gug' : 'v',

    'gcu' : 'a',
    'gcc' : 'a',
    'gca' : 'a',
    'gcg' : 'a',

    'gau' : 'd',
    'gac' : 'd',
    'gaa' : 'e',
    'gag' : 'e',

    'ggu' : 'g',
    'ggc' : 'g',
    'gga' : 'g',
    'ggg' : 'g',
    }

# Quick sanity check of genetic code structure
assert(len(genmap) == 4 * 4 * 4)
for k, v in genmap.items():
    for nucleotide in k:
        assert(nucleotide in nucleotides)
    assert(v in acids)
assert(set(genmap.values()) == acids)
del(k, v)


#
# Now read the SCN5A isoform a sequence (mRNA, encoded in DNA alphabet)
#
filename = 'mrna_human_scn5a_isoform1.txt'
print()
print('Loading SCN5A isoform a sequence from')
print('  ' + filename)

with open(filename, 'r') as f:
    scn5a = [line.strip() for line in f]
    scn5a = ''.join(scn5a[1:])

print('Read (' + str(len(scn5a)) + ') nucleotides, for (' + str(len(scn5a) / 3)
    + ') amino acids')


#
# To use this with the code above, we need to convert it to the lower case RNA
# alphabet
#
nucmap = {'A':'a', 'T':'u', 'C':'c', 'G':'g'}
scn5a = ''.join([nucmap[x] for x in scn5a])

#
# Now convert this to an amino acid sequence...
#

def find_start(sequence, offset=0):
    """
    Find the next start codon.
    """
    if start < 0:
        return -1
    start = scn5a.find('aug', offset)
    return start

def translate_section(sequence, start=0):
    """
    Translate a coding sequence embedded in a larger sequence.
    """
    if sequence[start:start+3] != 'aug':
        raise Exception('Coding segment must start with aug')
    nucs = iter(sequence[start:])
    i = 0
    protein = []
    for a in nucs:
        try:
            b, c = next(nucs), next(nucs)
        except StopIteration:
            return None, -1
        i += 3
        triplet = a + b + c
        acid = genmap[triplet]
        if acid == 'x':
            break
        protein.append(acid)
    return ''.join(protein), start + i

def translate(sequence, start=0):
    """
    Translate a coding sequence.
    """
    p, s = translate_section(sequence, start)
    return p

#
# First, extract the coding region
# NCBI says first region starts at 195 (for both isoform a and b)
# (Note 195 with start 1 equals 194 when indexing starts at 0)
#
start = 194

# Translate the section starting at `start`
default = translate(scn5a, start)
# Now use the length of this translated section to identify the coding
# sequence (again)
coding = scn5a[start:start + 3 * len(default)]
# It should be the same region as we found using translate_section!
assert(default == translate(coding))

# Now get the coding section, plus an extra nucleotide on each side
coding_plus = scn5a[start - 1:start + 3 * len(default) + 1]

#
# Show these results
#
print('Extracted coding sequence of ' + str(len(coding)) + ' bases long.')
print('  Start and end of coding sequence:')
print('  ' + coding[:30] + '...' + coding[-30:])
print()
print('Tested translation against reference translation: [OK]')
print('Resulting protein is ' + str(len(default)) + ' amino acids long.')
print('  Start and end of SCN5A, as translated:')
print('  ' + default[:30] + '...' + default[-30:])

#
# Load a stored SCN5A amino acid sequence, and compare
#
filename = 'isoform_a_NP_932173.1.txt'
print()
print('Loading known SCN5A sequence from')
print('  ' + filename)

with open(filename, 'r') as f:
    check = ''.join([x.strip() for x in f])
check = check.lower()
if check.lower() != default:
    raise Exception('Error translating default mRNA sequence')
print('Sequences match! Conversion is working.')


#
# Nucleotide substitution weights
# 'XY':1 means X to Y has weight 1
#
prime_weights = {
    'AC' : 9,
    'AG' : 32.8,
    'AT' : 7.5,
    'CG' : 8.9,
    'CT' : 32.8,
    'GT' : 9,
}
for key in list(prime_weights.keys()):
    prime_weights[key[::-1]] = prime_weights[key]
assert(len(prime_weights) == 12)

#
# Conditional substitution weight multipliers
# 'X' : 1.2 means X before/after nucleotide has multiplier 1.2
#
left_multipliers = {
    'A': 1.05,
    'C': 1.24,
    'G': 0.92,
    'T': 0.84,
}
right_multipliers = {
    'A': 0.85,
    'C': 0.92,
    'G': 1.25,
    'T': 1.03,
}

#
# Translate weights and multipliers to RNA alphabet
#
def nucmap_translate(d):
    for k1 in list(d.keys()):
        k2 = k1
        for dna, rna in nucmap.items():
            k2 = k2.replace(dna, rna)
        d[k2] = d[k1]
        del(d[k1])


nucmap_translate(prime_weights)
nucmap_translate(left_multipliers)
nucmap_translate(right_multipliers)

#
# Translate weights to easier structure for the next bit
#
x = prime_weights
prime_weights = {}
for nuc in nucmap.values():
    prime_weights[nuc] = {}
for sub, weight in x.items():
    old, new = sub
    prime_weights[old][new] = weight




#
# Create a list of weighted nucleotide substitutions on scn5a
#
print('Creating list of possible nucleotide substitutions')
scn5a_nuc_subs = []
for i, nuc in enumerate(coding):
    lm = left_multipliers[coding_plus[i]]
    rm = right_multipliers[coding_plus[i + 2]]
    for sub, weight in prime_weights[nuc].items():
        scn5a_nuc_subs.append((i, nuc, sub, weight * lm * rm))

# Show some statistics
import numpy as np
weights = np.array([x[3] for x in scn5a_nuc_subs])
print('Nucleotide substitutions:')
print('  Number possible: ' + str(len(weights)))
print('  Minimum weight : ' + str(np.min(weights)))
print('  Maximum weight : ' + str(np.max(weights)))
print('  Mean           : ' + str(np.mean(weights)))
print('  Sample std.    : ' + str(np.std(weights)))



#
# Add amino acid substitutions
#
print('Generating amino-acid substitutions')
#print(coding[:20])
scn5a_acid_subs = []
for i, nuc, sub, weight in scn5a_nuc_subs:

    # Get amino acid position (starting at 0)
    pos = i // 3

    # Get triplet
    ilo = 3 * pos
    iin = i - ilo
    iup = ilo + 3
    triplet = coding[ilo:iup]

    # Get mutant triplet
    mutant_triplet = triplet[:iin] + sub + triplet[iin + 1:]

    # Discard first triplet (must be start codon)
    if i < 3:
        continue

    # Get amino acids
    old = genmap[triplet]
    new = genmap[mutant_triplet]

    # Discard nonsense mutations
    if new == 'x':
        #print(i, nuc, sub, triplet, mutant_triplet, pos, old, new, 'stop')
        continue

    # Discard synonyms
    if new == old:
        #print(i, nuc, sub, triplet, mutant_triplet, pos, old, new, 'same')
        continue

    # Store solution
    #  - with position starting at 1
    #  - with weight from nucleotide substitution
    #  - with simple weight (each nuc sub counts once)
    #print(i, nuc, sub, triplet, mutant_triplet, pos, old, new)
    scn5a_acid_subs.append((1 + pos, old, new, weight))

print('  Count (including doubles): ' + str(len(scn5a_acid_subs)))


#
# Group doubles (summing their weight)
#
print('Summing weights for doubles')
from collections import OrderedDict
scn5a_mutations = OrderedDict()
scn5a_mutations_simple = OrderedDict()
for pos, old, new, weight in scn5a_acid_subs:
    try:
        scn5a_mutations[(pos, old, new)] += weight
        scn5a_mutations_simple[(pos, old, new)] += 1
    except KeyError:
        scn5a_mutations[(pos, old, new)] = weight
        scn5a_mutations_simple[(pos, old, new)] = 1
weights = np.array(list(scn5a_mutations.values()))
print('Unique mutations:')
print('  Count: ' + str(len(scn5a_mutations)))
print('  Minimum weight : ' + str(np.min(weights)))
print('  Maximum weight : ' + str(np.max(weights)))
print('  Mean           : ' + str(np.mean(weights)))
print('  Sample std.    : ' + str(np.std(weights)))


#
# Store the list of weighted mutations
#
filename = 'mutation_possible.csv'
print('Writing weighted mutations to')
print('  ' + filename)
# Store in list first, so we can sort it by (pos, new)
possible = []
for mut, weight in scn5a_mutations.items():
    simple = scn5a_mutations_simple[mut]
    pos, old, new = mut
    possible.append([str(x).upper() for x in (old, pos, new, weight, simple)])
possible.sort(key=lambda x: (int(x[1]), x[2]))
with open(filename, 'w') as f:
    f.write('old, idx, new, weight, simple_weight\n')
    for row in possible:
        f.write(', '.join(row) + '\n')

