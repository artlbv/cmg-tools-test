#!/usr/bin/env python

import glob, os
#from math import hypot
from ROOT import *
from searchBins import *
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
        return "%4.2f +- %4.2f" % (self.val, self.err)

class YieldStore:

    ## Class to store all yields from bin files
    ##
    ## Yields are stored in a dict with:
    ## -- key = (binName,category,sample) where category is SR_SB,Rcs,Kappa,etc
    ## -- value = (yield,error)

    def __init__(self,name):
        self.name = name

        self.yields = {} # yields in dictionary of type d[sample][category][bin] = (yield,err)
        self.bins = [] # list of all bins stored
        self.categories = [] # list of all categories available
        self.samples = [] # list of all samples available

    def addYield(self, sample, category, bin, yd):

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
        binName = bfname.replace(".merge.root","")
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

    def addFromFiles(self, pattern, leptype = ("lep","sele") ):

        # append / if pattern is a dir
        if os.path.isdir(pattern): pattern += "/"

        # find files matching pattern
        fileList = glob.glob(pattern+"*.root")

        print "Starting to add yields..."
        for fname in fileList:
            self.addBinYields(fname,leptype)
        print ".. finished"

        return 1

    def showStats(self):
        print 80*"#"
        print "Storage contains:"
        print len(self.bins), "Bins:", self.bins
        print len(self.categories), "Categories:", self.categories
        print len(self.samples), "Samples:", self.samples
        print 80*"#"

    ###########################
    ## Reading functions follow
    ###########################

    def getBinYield(self,samp,cat,bin):

        if samp in self.yields:
            if cat in self.yields[samp]:
                if bin in self.yields[samp][cat]:
                    return self.yields[samp][cat][bin]
        return 0

    def getSampDict(self,samp,cat):

        if samp in self.samples and cat in self.categories:
            return self.yields[samp][cat]
        else: return 0

    def getSampsDict(self,samp,cats = []):

        yds = {}

        for bin in self.bins:
            yds[bin] = []
            for cat in cats:
                yds[bin].append(self.getBinYield(samp,cat,bin))
        return yds

    def getMixDict(self, samps = []):
        # provide dict: sample - category
        # return dict: bin - yields (corresp to sample,cat)

        yds = {}
        for bin in self.bins:
            yds[bin] = []

            for samp,cat in samps:
                yds[bin].append(self.getBinYield(samp,cat,bin))

        return yds

    def printBins(self, samp,cat):
        if type(cat) == str:
            yds = self.getSampDict(samp,cat)
        elif type(cat) == list:
            yds = self.getSampsDict(samp,cat)
        else:
            print "You have to give either a string or a list of strings"
            return 0

        print 80*"-"
        print "Contents for sample %s and category %s" %(samp,cat)
        #print "Bin\tYield+-Error"

        for bin in sorted(yds.keys()):
            print bin,"\t", yds[bin]
        print 80*"-"

        return 1

    def printMixBins(self, samps):

        yds = self.getMixDict(samps)

        print 80*"-"
        print "Contents for", samps
        print "Bin\tYield+-Error"

        for bin in sorted(yds.keys()):
            print bin,"\t\t",
            for yd in yds[bin]: print yd,"\t",
            print

        return 1

    def printLatexTable(self, samps, printSamps, label, f):
        yds = self.getMixDict(samps)
        nSource = len(samps)
        nCol = nSource + 4
        precision = 5
        f.write('\multicolumn{' + str(nCol) + '}{|c|}{' +label +'} \\\ \\hline \n')
        f.write('$L_T$ & $H_T$ & nB & binName &' +  ' %s ' % ' & '.join(map(str, printSamps)) + ' \\\ \n')
        f.write(' $[$ GeV $]$  &   $[$GeV$]$ & &  '  + (nSource *'%(tab)s  ') % dict(tab = '&') + ' \\\ \\hline \n')

        bins = sorted(yds.keys())
        for i,bin in enumerate(bins):
            (LTbin, HTbin, Bbin ) = bin.split("_")[0:3]        
            (LT, HT, B) = (binsLT[LTbin][1],binsHT[HTbin][1],binsNB[Bbin][1])           
            (LT0, HT0, B0 ) = ("","","") 
            if i > 0 :
                (LT0bin, HT0bin, B0bin ) = bins[i-1].split("_")[0:3]
                (LT0, HT0, B0) = (binsLT[LT0bin][1],binsHT[HT0bin][1],binsNB[B0bin][1])           
            if LT != LT0:
                f.write(('\\cline{1-%s} ' + LT + ' & ' + HT + ' & ' + B + '&' + LTbin +', ' + HTbin + ', ' + Bbin) % (nCol))
            if LT == LT0 and HT != HT0:
                f.write(('\\cline{2-%s}  & ' + HT + ' & ' + B + '&' + LTbin +', ' + HTbin + ', ' + Bbin) % (nCol))
            elif LT == LT0 and HT == HT0:
                f.write('  &  & ' + B + '&' + LTbin +', ' + HTbin + ', ' + Bbin)

            for yd in yds[bin]:
                f.write((' & %.'+str(precision)+'f $\pm$ %.'+str(precision)+'f') % (yd.val, yd.err))
            
            f.write(' \\\ \n')
        f.write(' \\hline \n')
        return 1


if __name__ == "__main__":

    #pattern = "Yields/wData/lumi1p2_puWeight_data/grid/merged/LT1_HT0_NB0*NJ68"
    #pattern = "Yields/wData/lumi1p2_puWeight_data/grid/merged/LT1_HT0_NB*NJ68"
    pattern = "Yields/wData/lumi1p2_puWeight_data/grid/merged/LT*NJ68"

    fileList = glob.glob(pattern+"*.root")

    yds = YieldStore("bla")
    yds.addFromFiles(pattern)

    #print yds.bins
    print yds.categories
    print yds.samples
    #yds.printBins("QCD","CR_SB")
    #yds.getSampsDict("QCD",["CR_SB","CR_MB"])
    #yds.printBins("QCD",["CR_SB","CR_MB"])
    #yds.printBins("data",yds.categories)

    #samps = {"EWK":"CR_MB","QCD":"CR_SB"}
    #samps = {"EWK":"CR_SB","background_QCDsubtr":"CR_SB","background_QCDsubtr":"Closure"}
    samps = [
        ("QCD","CR_SB"),
        ("QCD_QCDpred","CR_SB"),
        ("QCD_QCDsubtr","CR_SB"),
        ]
    #print yds.getMixDict(samps)
    yds.printMixBins(samps)

    #print yds.yields
