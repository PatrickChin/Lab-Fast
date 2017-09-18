import os
import numpy as np
from lowtempcal import LowTempCalData

def tobin(infile, outfile, overwrite=False):
    bintype = np.dtype([('time',np.int), ('current',np.float),
                         ('voltage',np.float), ('temperature',np.float)])

    infile = os.path.abspath(infile)
    outfile = os.path.abspath(outfile)

    if not overwrite and os.path.exists(outfile):
        return

    outdir = os.path.dirname(outfile)
    if not os.path.isdir(outdir):
        print("Creating directory: ", outdir)
        os.mkdir(outdir)

    data = np.loadtxt(infile, delimiter=',',
            dtype=LowTempCalData.dtype)
    data.tofile(outfile)
