#!/usr/bin/env python
#
# Draw diagrams of SCN5A based on a few fixed points connected with bezier
# curves.
#
# The code to draw bezier curves is based on:
#  1. http://www.hannahfry.co.uk/blog/2011/11/16/bezier-curves
#  2. http://math.stackexchange.com/questions/15896
#
from __future__ import print_function
import numpy as np
import matplotlib.pyplot as pl

debug = True
if debug:
    print()

# Read in the origin & destination points
rows = []
data = []
with open('positions.csv', 'r') as f:
    f.next() # Skip header
    for row in f:
        fields = row.split(',')
        rows.append(fields)
        data.append([float(x) for x in fields[1:5]]) # x,y,angle,length
        
# Create data array
data = np.array(data)

# Convert angles
data[:, 2] *= np.pi / 180

# Create dict for points {id : (x, y)}
points = {}

# Create a figure
pl.figure()

# Draw a bezier curve for each set of points
i0 = iter(data)
i1 = iter(data)
i1.next()
for i in xrange(len(rows) - 1):
    x0, y0, a0, n0 = i0.next()
    x1, y1, a1, n1 = i1.next()
    n = n1 + 1

    # Guess control points
    r = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    if n < 15:
        r *= 0.8
    else:
        r *= 0.25
    cx0 = x0 + r * np.cos(a0)
    cy0 = y0 + r * np.sin(a0)
    cx1 = x1 + r * np.cos(a1 + np.pi)
    cy1 = y1 + r * np.sin(a1 + np.pi)
    
    # Plot the points and control points
    if debug:
        pl.plot(x0, y0, 'ok')
        pl.plot(x1, y1, 'ok')
        pl.plot((x0, cx0), (y0, cy0), 'b')
        pl.plot((x1, cx1), (y1, cy1), 'g')
    
    # Approximate equidistance points on a bezier curve
    t = np.linspace(0, 1, n)
    for j in xrange(1000): # Guess at required number of iterations
        # Calculate points at given t's
        b0 = (1 - t)**3
        b1 = 3 * (1 - t)**2 * t
        b2 = 3 * (1 - t) * t**2
        b3 = t**3
        x = b0 * x0 + b1 * cx0 + b2 * cx1 + b3 * x1
        y = b0 * y0 + b1 * cy0 + b2 * cy1 + b3 * y1
        # Update t's to get equidistant points
        q = t
        for k in xrange(1, len(t) - 1):
            # Calculate distance to previous point, next point
            d1 = ((x[k-1]-x[k])**2 + (y[k-1]-y[k])**2)**0.5
            d2 = ((x[k+1]-x[k])**2 + (y[k+1]-y[k])**2)**0.5
            # Select new point halfway in the right direction
            ff = 0.5 * (d2 - d1) / (d2 + d1)
            if ff > 0:
                q[k] += ff * (t[k+1] - t[k])
            else:
                q[k] += ff * (t[k] - t[k-1])
        t = q
    # Show mean distance in segment
    if debug:
        d = ((x[1:]-x[:-1])**2 + (y[1:]-y[:-1])**2)**0.5
        print(rows[i][0] + ' - ' + rows[i+1][0])
        print('  ' + str(np.mean(d)) + ', ' + str(np.std(d)))
        
    for k in xrange(len(x)):
        pid = int(rows[i][0]) + k
        points[pid] = (x[k], y[k])

    # Plot the curve
    pl.plot(x, y, 'ob')
    
# Store points
with open('scn5a_diagram.csv', 'w') as f:
    f.write('idx,x,y\n')
    for pid in sorted(points.keys()):
        data = points[pid]
        data = [pid, data[0], data[1]]
        f.write(','.join([str(x) for x in data]) + '\n')

# Set nice limits for viewing
pl.axes().set_aspect('equal', 'datalim')
xlim = pl.xlim()
ylim = pl.ylim()
pl.xlim(xlim[0]-1, xlim[1]+1)
pl.ylim(ylim[0]-1, ylim[1]+1)

# Show
pl.show()

