import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

muondata = np.loadtxt("data.txt", delimiter=' ', dtype=int)[:,0]

muondata1 = [s for s in muondata if s > 60 and s < 40000]
hist, edges = np.histogram(muondata1, bins=20)
mids = (edges[1:] + edges[:-1]) / 2
loghist = np.log(hist)

def func(x, a, b, c):
    return np.log(a * np.exp(-x/b) + c)

popt, pvov = curve_fit(func, mids, loghist, (2000, 2200, 6), loghist/2)
print(popt)

a = np.transpose([mids, hist])

print(a)

plt.plot(mids,loghist,'b.')
plt.show()
