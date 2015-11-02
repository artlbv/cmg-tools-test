#!/usr/bin/env python

import glob, os, sys
#from math import hypot
from ROOT import *

def getLepYield(hist,leptype = ('lep','sele')):

    if hist.GetNbinsX() == 1:
        return (hist.GetBinContent(1),hist.GetBinError(1))

    elif hist.GetNbinsX() == 3 and hist.GetNbinsY() == 2:

        if leptype == ('mu','anti'):
            return (hist.GetBinContent(1,1),hist.GetBinError(1,1))
        elif leptype == ('mu','sele'):
            return (hist.GetBinContent(1,2),hist.GetBinError(1,2))
        elif leptype == ('ele','anti'):
            return (hist.GetBinContent(3,1),hist.GetBinError(3,1))
        elif leptype == ('ele','sele'):
            return (hist.GetBinContent(3,2),hist.GetBinError(3,2))
        elif leptype == ('lep','anti'):
            return (hist.GetBinContent(2,1),hist.GetBinError(2,1))
        elif leptype == ('lep','sele'):
            return (hist.GetBinContent(2,2),hist.GetBinError(2,2))
    else:
        return (hist.Integral(),TMath.sqrt(hist.Integral()))


class BinYields:

    def __init__(self,name):
        self.name = name
        self.yDict = {} # yields in dictionary

    def addBin(self, fname, leptype = ("lep","sele")):

        binDict = {}

        tfile = TFile(fname,"READ")


        bfname = os.path.basename(fname)
        binName = bfname.replace("_SR.merge.root","")

        # get list of dirs
        dirList = [dirKey.ReadObj() for dirKey in gDirectory.GetListOfKeys() if dirKey.IsFolder() == 1]

        for ydir in dirList:
            ydir.cd()

            # get list of histograms
            histList = [histKey.ReadObj() for histKey in gDirectory.GetListOfKeys() if histKey.IsFolder() != 1]
            ydDict = {hist.GetName(): getLepYield(hist) for hist in histList}
            #ydDict = {hist.GetName(): (0,0) for hist in histList}
            #print ydDict
            #print histList

            binDict[ydir.GetName()] = ydDict

        # update ydDict with current bin
        self.yDict[binName] = binDict

    def printSamp(self, sname, ytype = "CR_MB"):

        print 40*"/\\"
        print "Values for %s in %s" %(sname,ytype)
        print 80*"-"
        for bin,tDict in self.yDict.iteritems():
            #print 80*"#"
            #print 'tdict in ', bin,'is', tDict

            if ytype in tDict:
                hDict = tDict[ytype]
                if sname in hDict:
                    print "%s\t%.2f" %(bin,  hDict[sname][0])

        print 40*"\\/"

if __name__ == "__main__":

    pattern = "Yields/wData/lumi1p2_puWeight_data/grid/merged/LT*NJ68"
    fileList = glob.glob(pattern+"*.root")

    by = BinYields("bla")

    for fname in fileList:
        by.addBin(fname)

    #print by.yDict
    by.printSamp("QCD")

    by.printSamp("EWK")
