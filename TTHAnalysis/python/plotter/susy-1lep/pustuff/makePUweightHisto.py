#!/usr/bin/env python
import sys

from math import *
from ROOT import *

def getPUratio(fdata, fmc, hname = "puRatio"):

    hdata = fdata.Get("pileup")
    hmc = fmc.Get("")


if __name__ == "__main__":

    '''
    if '-b' in sys.argv:
        sys.argv.remove('-b')
        _batchMode = True
    '''

    if len(sys.argv) > 2:
        dataFname = sys.argv[1]
        mcFname = sys.argv[2]

        print '## data file:', dataFname
        print '## mc   file:', mcFname

    else:
        print "## Usage:"
        print "./makePUweightHisto.py dataPUfile.root mcPUfile.root"
        exit(0)

    fdata  = TFile(dataFname, "READ")
    fmc  = TFile(mcFname, "READ")
    fout  = TFile("pu_ratio.root", "RECREATE")

    if not fdata or not fmc:
        print "Couldn't open the file(s)"
        exit(0)

    ## Get tree from file
    # for friend trees
    tree = tfile.Get('sf/t')
    # for cmg trees
    #tree = tfile.Get('tree')

    dumpCounts(tree)


    fdata.Close()
    fmc.Close()
    fout.Close()

    print 'Finished'
