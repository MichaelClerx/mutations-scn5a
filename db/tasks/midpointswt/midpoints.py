#!/usr/bin/env python3
#
# Creates data for a graph of V1/2 of activation & inactivation of wild-type
# channels in expression systems and myocyte data.
#
import base
import numpy as np
import scipy as sp
import scipy.stats
import matplotlib.pyplot as pl
DEBUG = False
def tasks():
    """
    Returns a list of the tasks in this file.
    """
    return [
        MidpointsWT(),
        MidpointsMyo(),
        WeightedMidpointsWT(),
        WeightedMidpointsMyo(),
        ]
def gaussian(x, mu, sigma):
    """
    Return a gaussian/normal pdf over x, with mean mu and stddev sigma.
    """
    return 1.0 / (sigma * np.sqrt(2.0 * np.pi)) * np.exp(
        -np.power((x - mu) / sigma, 2.0) * 0.5)
class Midpoints(base.Task):
    def __init__(self, name):
        super(Midpoints, self).__init__(name)
        self._set_data_subdir('midpointswt')
    def gather(self, filename, rows, weighted):
        """
        Takes a series of rows, each with five columns in the order
        ``(name, v, sem, n, std)``, calculates the resulting probability
        density functions and writes them to the csv file ``filename``, along
        with a summed version called 'sum' and a fit to the sum, called 'fit'
        and finally a field called 'x' with the voltages for each point.
        
        Sums will be either weighted or unweighted.
        """
        # High number of x-axis points, for accurate calculations
        npoints = 100000
        # Lower number of points, for fast representations
        xf = int(npoints / 1000)
        # Create x-data and y-data
        x = np.linspace(-140, 20, npoints)
        y = np.zeros(x.shape)
        # Multiplier for calculating sums
        dx = x[1] - x[0]
        # Debug code
        if DEBUG:
            pl.figure()
        # Names of each measurement
        fields = []
        # Result for each measurement (v, std, n)
        data = {}
        # Total number of cells measured
        ntotal = 0
        # Gather data from rows
        for k, row in enumerate(rows):
            pub, v, sem, n, std = row
            field = str(k) + '-' + pub
            # Skip rows without act/inact measurement
            if n == 0:
                continue
            # Check std calculation
            if np.abs(std - sem * np.sqrt(n)) > 1e-6:
                print('Warning: Error in STD for ' + field)
                print('  Listed    : ' + str(s))
                print('  Calculated: ' + str(s * np.sqrt(n)))
            # Update ntotal
            ntotal += n
            # Store data
            fields.append(field)
            data[field] = (v, std, n)
        # Create probability density functions
        nmeasurements = len(fields)
        pdfs = {}
        for field in fields:
            v, std, n = data[field]
            # Create pdf
            if weighted:
                pdf = (float(n) / ntotal) * gaussian(x, v, std)
            else:
                pdf = (1.0 / nmeasurements) * gaussian(x, v, std)
            # Update sum
            y += pdf
            # Store reduced data
            pdfs[field] = pdf[::xf]
            # Debug plot
            if DEBUG:
                color = pl.plot(x[::xf], pdf[::xf])[0].get_color()
                pl.fill_between(x[::xf], 0, pdf[::xf], color=color, alpha=0.2)
                pl.axvline(v, 0, 1, color=color, alpha=0.4)
        print('Collected data from ' + str(nmeasurements) + ' measurements in '
            + str(ntotal) + ' cells!')
        print('Area under sum curve: ' + str(np.sum(y) * dx))
        # Calculate mean and standard deviation
        mu = np.sum(x * y) / np.sum(y)
        sigma = np.sqrt(np.sum(y * ((x - mu) ** 2)) / np.sum(y))
        print('Mean: ' + str(mu))
        print('Stddev: ' + str(sigma))
        print('2Sigma-range: [' + str(mu-2*sigma) + ',' + str(mu+2*sigma) +']')
        # Test goodness of fit using a chi-squared test
        z = gaussian(x, mu, sigma)
        chisq,p = sp.stats.chisquare(
            y/np.sum(y),
            z/np.sum(z),
            2,  # 2 params used to estimate z
            ) 
        print('Normal: ' + str(p))
        # Reduce data
        x = x[::xf]
        y = y[::xf]
        # Draw gaussian curve
        z = gaussian(x, mu, sigma)
        # Debug plot
        if DEBUG:
            pl.plot(x, y, lw=2)
            pl.plot(x, z, lw=2)
        # Write file
        print('Writing to ' + filename)
        with open(filename, 'w') as f:
            csv = self.csv_writer(f)
            csv.writerow(fields + ['sum', 'gauss', 'x'])
            data = []
            for field in fields:
                data.append(iter(pdfs[field]))
            data.append(iter(y))
            data.append(iter(z))
            data.append(iter(x))
            for i in range(len(x)):
                csv.writerow([next(j) for j in data])
class MidpointsWT(Midpoints):
    def __init__(self):
        super(MidpointsWT, self).__init__('midpoints_wt')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            # Activation: All data
            print('== Activation: all data')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            filename = 'midpoints-f-wt-a-00-all.csv' # f for flat
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: Isoform a
            print('== Activation: isoform a')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence == "a"'
            filename = 'midpoints-f-wt-a-01-isoform-a.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: Isoform b
            print('== Activation: isoform b')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence == "b"'
            filename = 'midpoints-f-wt-a-02-isoform-b.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: Isoform a*
            print('== Activation: isoform a*')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence == "astar"'
            filename = 'midpoints-f-wt-a-03-isoform-a-star.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: Isoform b*
            print('== Activation: isoform b*')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence == "bstar"'
            filename = 'midpoints-f-wt-a-04-isoform-b-star.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: Unknown isoform
            print('== Activation: isoform unknown')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence is null'
            filename = 'midpoints-f-wt-a-05-isoform-unknown.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: HEK
            print('== Activation: HEK')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where cell == "HEK"'
            filename = 'midpoints-f-wt-a-06-hek.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: Oocytes
            print('== Activation: Oocytes')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where cell == "Oocyte"'
            filename = 'midpoints-f-wt-a-07-oocytes.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: CHO
            print('== Activation: CHO')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where cell == "CHO"'
            filename = 'midpoints-f-wt-a-08-cho.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: With beta1
            print('== Activation: With beta1')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where beta1 == "yes"'
            filename = 'midpoints-f-wt-a-09-with-beta1.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: Without beta1
            print('== Activation: Without beta1')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where beta1 == "no"'
            filename = 'midpoints-f-wt-a-10-without-beta1.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: HEK, a*, with
            print('== Activation: Most common: HEK, a*, with')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence == "astar"'
            q += ' and cell == "HEK"'
            q += ' and beta1 == "yes"'
            filename = 'midpoints-f-wt-a-11-most-common.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            #
            # Inactivation
            #
            # Inactivation: All data
            print('== Inactivation: all data')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            filename = 'midpoints-f-wt-i-00-all.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Inactivation: Isoform a
            print('== Inactivation: isoform a')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence == "a"'
            filename = 'midpoints-f-wt-i-01-isoform-a.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Inactivation: Isoform b
            print('== Inactivation: isoform b')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence == "b"'
            filename = 'midpoints-f-wt-i-02-isoform-b.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Inactivation: Isoform a
            print('== Inactivation: isoform a*')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence == "astar"'
            filename = 'midpoints-f-wt-i-03-isoform-a-star.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Inactivation: Isoform b
            print('== Inactivation: isoform b*')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence == "bstar"'
            filename = 'midpoints-f-wt-i-04-isoform-b-star.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: Isoform unknown            
            print('== Inctivation: isoform unknown')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence is null'
            filename = 'midpoints-f-wt-i-05-isoform-unknown.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Inactivation: HEK
            print('== Inactivation: HEK')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where cell == "HEK"'
            filename = 'midpoints-f-wt-i-06-hek.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: Oocytes
            print('== Inactivation: Oocytes')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where cell == "Oocyte"'
            filename = 'midpoints-f-wt-i-07-oocytes.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Activation: CHO
            print('== Inactivation: CHO')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where cell == "CHO"'
            filename = 'midpoints-f-wt-i-08-cho.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Inactivation: With beta1
            print('== Inactivation: With beta1')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where beta1 == "yes"'
            filename = 'midpoints-f-wt-i-09-with-beta1.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Inactivation: Without beta1
            print('== Inactivation: Without beta1')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where beta1 == "no"'
            filename = 'midpoints-f-wt-i-10-without-beta1.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Inactivation: HEK, a*, with
            print('== Inactivation: Most common: HEK, a*, with')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence == "astar"'
            q += ' and cell == "HEK"'
            q += ' and beta1 == "yes"'
            filename = 'midpoints-f-wt-i-11-most-common.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
        #
        # Show debug graphs
        #
        if DEBUG:
            pl.show()
class WeightedMidpointsWT(Midpoints):
    def __init__(self):
        super(WeightedMidpointsWT, self).__init__('midpoints_w_wt')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            # Activation: All data
            print('== Activation: all data, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            filename = 'midpoints-w-wt-a-00-all.csv' # w for weighted
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: Isoform a
            print('== Activation: isoform a, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence == "a"'
            filename = 'midpoints-w-wt-a-01-isoform-a.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: Isoform b
            print('== Activation: isoform b, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence == "b"'
            filename = 'midpoints-w-wt-a-02-isoform-b.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: Isoform a*
            print('== Activation: isoform a*, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence == "astar"'
            filename = 'midpoints-w-wt-a-03-isoform-a-star.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: Isoform b*
            print('== Activation: isoform b*, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence == "bstar"'
            filename = 'midpoints-w-wt-a-04-isoform-b-star.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: Isoform unknown
            print('== Activation: isoform unknown, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence is null'
            filename = 'midpoints-w-wt-a-05-isoform-unknown.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: HEK
            print('== Activation: HEK, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where cell == "HEK"'
            filename = 'midpoints-w-wt-a-06-hek.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: Oocytes
            print('== Activation: Oocytes, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where cell == "Oocyte"'
            filename = 'midpoints-w-wt-a-07-oocytes.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: CHO
            print('== Activation: CHO, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where cell == "CHO"'
            filename = 'midpoints-w-wt-a-08-cho.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: With beta1
            print('== Activation: With beta1, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where beta1 == "yes"'
            filename = 'midpoints-w-wt-a-09-with-beta1.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: Without beta1
            print('== Activation: Without beta1, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where beta1 == "no"'
            filename = 'midpoints-w-wt-a-10-without-beta1.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: HEK, a*, beta1
            print('== Activation: Most common: HEK, a*, beta1, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_wt'
            q += ' where sequence == "astar"'
            q += ' and cell == "HEK"'
            q += ' and beta1 == "yes"'
            filename = 'midpoints-w-wt-a-11-most-common.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            #
            # Inactivation
            #
            # Inactivation: All data
            print('== Inactivation: all data, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            filename = 'midpoints-w-wt-i-00-all.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Inactivation: Isoform a
            print('== Inactivation: isoform a, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence == "a"'
            filename = 'midpoints-w-wt-i-01-isoform-a.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Inactivation: Isoform b
            print('== Inactivation: isoform b, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence == "b"'
            filename = 'midpoints-w-wt-i-02-isoform-b.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Inactivation: Isoform a
            print('== Inactivation: isoform a*, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence == "astar"'
            filename = 'midpoints-w-wt-i-03-isoform-a-star.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Inactivation: Isoform b
            print('== Inactivation: isoform b*, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence == "bstar"'
            filename = 'midpoints-w-wt-i-04-isoform-b-star.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Inactivation: Isoform unknown
            print('== Inactivation: isoform unknown, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence is null'
            filename = 'midpoints-w-wt-i-05-isoform-unknown.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Inactivation: HEK
            print('== Inactivation: HEK, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where cell == "HEK"'
            filename = 'midpoints-w-wt-i-06-hek.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: Oocytes
            print('== Inactivation: Oocytes, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where cell == "Oocyte"'
            filename = 'midpoints-w-wt-i-07-oocytes.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Activation: CHO
            print('== Inactivation: CHO, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where cell == "CHO"'
            filename = 'midpoints-w-wt-i-08-cho.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Inactivation: With beta1
            print('== Inactivation: With beta1, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where beta1 == "yes"'
            filename = 'midpoints-w-wt-i-09-with-beta1.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Inactivation: Without beta1
            print('== Inactivation: Without beta1, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where beta1 == "no"'
            filename = 'midpoints-w-wt-i-10-without-beta1.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Inactivation: HEK, a*, with
            print('== Inactivation: Most common: HEK, a*, beta1, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_wt'
            q += ' where sequence == "astar"'
            q += ' and cell == "HEK"'
            q += ' and beta1 == "yes"'
            filename = 'midpoints-w-wt-i-11-most-common.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
        #
        # Show debug graphs
        #
        if DEBUG:
            pl.show()
class MidpointsMyo(Midpoints):
    def __init__(self):
        super(MidpointsMyo, self).__init__('midpoints_myo')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            # Activation: All data
            print('== Activation: all data')
            q = 'select pub, va, sema, na, stda from midpoints_myo'
            filename = 'midpoints-f-myo-a-00-all.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
            # Inactivation: All data
            print('== Inactivation: all data')
            q = 'select pub, vi, semi, ni, stdi from midpoints_myo'
            filename = 'midpoints-f-myo-i-00-all.csv'
            self.gather(self.data_out(filename), c.execute(q), False)
        #
        # Show debug graphs
        #
        if DEBUG:
            pl.show()
class WeightedMidpointsMyo(Midpoints):
    def __init__(self):
        super(WeightedMidpointsMyo, self).__init__('midpoints_w_myo')
    def _run(self):
        with base.connect() as con:
            c = con.cursor()
            # Activation: All data
            print('== Activation: all data, weighted')
            q = 'select pub, va, sema, na, stda from midpoints_myo'
            filename = 'midpoints-w-myo-a-00-all.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
            # Inactivation: All data
            print('== Inactivation: all data, weighted')
            q = 'select pub, vi, semi, ni, stdi from midpoints_myo'
            filename = 'midpoints-w-myo-i-00-all.csv'
            self.gather(self.data_out(filename), c.execute(q), True)
        #
        # Show debug graphs
        #
        if DEBUG:
            pl.show()

if __name__ == '__main__':
    #DEBUG = True
    runner = base.TaskRunner()
    runner.add_tasks(tasks())
    runner.run()
