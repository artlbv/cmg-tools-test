#!/usr/bin/env python
import sys

from math import *
from ROOT import *

def dumpCounts(tree):

    hScan = TH2F("hScan","Mass scan",1000,1,2001,1000,-1,2001)

    #var = "mLSP:mGo" # for friend tree
    var = "GenSusyMNeutralino:GenSusyMGluino" # for cmg tuple

    tree.Draw(var + '>>' + hScan.GetName(),"","goff")

    totalEvts = hScan.GetEntries()

    print hScan

    print 'Total produced events:', totalEvts

    cntDict = {}

    # round up to 5
    base = 5

    for xbin in range(1,hScan.GetNbinsX()+1):
        for ybin in range(1,hScan.GetNbinsY()+1):

            cnt = hScan.GetBinContent(xbin,ybin)
            if cnt == 0: continue

            mGo = hScan.GetXaxis().GetBinCenter(xbin)
            #mGo = hScan.GetXaxis().GetBinLowEdge(xbin)
            mLSP = hScan.GetYaxis().GetBinCenter(ybin)
            #mLSP = hScan.GetYaxis().GetBinLowEdge(ybin)

            # round up to base (5)
            mGo = int(base * round(mGo/base))
            mLSP = int(base * round(mLSP/base))

            #print "Found %i entries for mass point %i,%i" %(cnt, mGo,mLSP)
            cntDict[(mGo,mLSP)] = cnt

    # write file
    with open("counts.txt","w") as cfile:

        cfile.write("Total\t" + str(totalEvts) + "\n")
        cfile.write("#mGo\tmLSP\tcounts\n")

        for point in cntDict:
            if cntDict[point] > 0:
                line = "%i\t%i\t%i\n" %(point[0],point[1],cntDict[point])
                cfile.write(line)

    #raw_input("exit")

def dumpTree(fileName):
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

def dumpChain(fileList):

    #ch = TChain("sf/t")
    ch = TChain("tree")

    for f in fileList:
        ch.Add(f)

    print "Got %i files" % len(fileList),
    print "with %i events" % ch.GetEntries()

    dumpCounts(ch)

if __name__ == "__main__":

    if '-b' in sys.argv:
        sys.argv.remove('-b')

    if len(sys.argv) > 1:
        fileList = sys.argv[1:]
        #print '#fileName is', fileName
    else:
        print '#No file names given'
        exit(0)

    dumpChain(fileList)

    print 'Finished'
