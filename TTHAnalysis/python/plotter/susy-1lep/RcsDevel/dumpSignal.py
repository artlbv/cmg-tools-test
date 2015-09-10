#!/usr/bin/env python
import sys

from math import *
from ROOT import *

def dumpCounts(tree):

    hScan = TH2F("hScan","Mass scan",30,0,1500,30,0,1500)

    var = "mLSP:mGo" # for friend tree
    #var = "GenSusyMNeutralino:GenSusyMGluino" # for cmg tuple

    tree.Draw(var + '>>' + hScan.GetName())

    totalEvts = hScan.GetEntries()

    print hScan

    print 'Total produced events:', totalEvts

    cntDict = {}

    for xbin in range(1,hScan.GetNbinsX()+1):
        for ybin in range(1,hScan.GetNbinsY()+1):

            #mGo = hScan.GetXaxis().GetBinCenter(xbin)
            mGo = hScan.GetXaxis().GetBinLowEdge(xbin)
            #mLSP = hScan.GetYaxis().GetBinCenter(ybin)
            mLSP = hScan.GetYaxis().GetBinLowEdge(ybin)
            cnt = hScan.GetBinContent(xbin,ybin)

            #print "Found %i entries for mass point %i,%i" %(cnt, mGo,mLSP)
            cntDict[(mGo,mLSP)] = cnt

    # write file
    with open("counts.txt","w") as cfile:

        cfile.write("Total\t" + str(totalEvts) + "\n")
        cfile.write("#mGo\tmLSP\tcounts\n")

        for point in cntDict:
            line = "%i\t%i\t%i\n" %(point[0],point[1],cntDict[point])
            cfile.write(line)

if __name__ == "__main__":

    ## remove '-b' option
    _batchMode = False

    if '-b' in sys.argv:
        sys.argv.remove('-b')
        _batchMode = True

    if len(sys.argv) > 1:
        fileName = sys.argv[1]
        print '#fileName is', fileName
    else:
        print '#No file names given'
        exit(0)

    tfile  = TFile(fileName, "READ")

    if not tfile:
        print "Couldn't open the file"
        exit(0)

    ## Get tree from file
    # for friend trees
    tree = tfile.Get('sf/t')
    # for cmg trees
    #tree = tfile.Get('tree')

    dumpCounts(tree)


    tfile.Close()

    print 'Finished'
