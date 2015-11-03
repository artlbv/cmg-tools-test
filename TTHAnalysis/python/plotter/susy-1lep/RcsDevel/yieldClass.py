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

class BinYield:
    ## Simple class for yield,error storing (instead of tuple)

    def __init__(self, (val, err)):
        self.val = val
        self.err = err

    def __repr__(self):
        return "%.3f +- %.3f" % (self.val, self.err)

class YieldStore:

    ## Class to store all yields from bin files
    ##
    ## Yields are stored in a dict with:
    ## -- key = (binName,category,sample) where category is SR_SB,Rcs,Kappa,etc
    ## -- value = (yield,error)

    def __init__(self,name):
        self.name = name
        self.yDict = {} # yields in dictionary

        self.yields = {} # yields in dictionary of type d[sample][category][bin] = (yield,err)
        self.bins = [] # list of all bins stored
        self.categories = [] # list of all categories available
        self.samples = [] # list of all samples available

    def addYield(self, sample, category, bin, yd):
        '''
        yields = {} # dict of type d[sample] = catDict
        samples = {} # dict of type d[sample] = categoryDict
        categories = {} # d[category] = binDict
        bins = {} # d[bin] = (yield,err)
        '''

        # create dict structure if empty and add to list storages
        if sample not in self.yields: self.yields[sample] = {}
        if sample not in self.samples: self.samples.append(sample)

        if category not in self.yields[sample]: self.yields[sample][category] = {}
        if category not in self.categories:     self.categories.append(category)

        if bin not in self.bins: self.bins.append(bin)

        # add bin yield
        self.yields[sample][category][bin] = yd
        #print "Adding", sample, category, bin, "with", yd

        return 1

    def addBinYields(self, fname, leptype = ("lep","sele")):

        # Open file and get bin name
        tfile = TFile(fname,"READ")
        bfname = os.path.basename(fname)
        binName = bfname.replace("_SR.merge.root","")
        #print binName

        # get list of dirs
        dirList = [dirKey.ReadObj() for dirKey in gDirectory.GetListOfKeys() if dirKey.IsFolder() == 1]

        for catDir in dirList:
            catDir.cd()

            category = catDir.GetName()

            # get list of histograms
            histList = [histKey.ReadObj() for histKey in gDirectory.GetListOfKeys() if histKey.IsFolder() != 1]

            ## Loop over hists and save to dicts
            for hist in histList:

                sample = hist.GetName()

                yd = BinYield(getLepYield(hist, leptype))

                self.addYield(sample,category,binName,yd)
        return 1

    def getBinDict(self,samp,cat):

        if samp in self.samples and cat in self.categories:
            return self.yields[samp][cat]

    def printSamp(self, sname, ytype = "CR_MB"):

        print 40*"/\\"
        print "Values for %s in %s" %(sname,ytype)
        print 80*"-"
        print 40*"\\/"

if __name__ == "__main__":

    pattern = "Yields/wData/lumi1p2_puWeight_data/grid/merged/LT1_HT0_NB*NJ68"
    fileList = glob.glob(pattern+"*.root")

    by = YieldStore("bla")

    for fname in fileList:
        by.addBinYields(fname)

    #print by.yDict
    #by.printSamp("QCD")

    #by.printSamp2("EWK")

    print by.bins
    print by.categories
    print by.samples

    print by.getBinDict("QCD","CR_SB")
