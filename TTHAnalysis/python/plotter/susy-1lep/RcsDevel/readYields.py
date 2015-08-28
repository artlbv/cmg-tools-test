#!/usr/bin/env python
#import re, sys, os, os.path
#from searchBins import *
import glob, os, sys
from ROOT import *


def addOptions(options):

    # set tree options
    options.path = Tdir
    options.friendTrees = [("sf/t",FTdir+"/evVarFriend_{cname}.root")]
    options.tree = "treeProducerSusySingleLepton"

    # extra options
    options.doS2V = True
    options.weight = True
    options.final  = True
    options.allProcesses  = True
    #options.maxEntries = 10000

    # signal scan
    if options.signal:
        options.var =  "mLSP:mGo"
        options.bins = "30,0,1500,30,0,1500"
        options.friendTrees = [("sf/t","FriendTrees_MC/evVarFriend_{cname}.root")]

def getYield(tfile,hname = "x_T1tttt_HM_1200_800"):

    hist = tfile.Get(hname)

    if hist.GetNbinsX() == 1:
        return (hist.GetBinContent(1),hist.GetBinError(1))
    else:
        return (hist.Integral(),TMath.sqrt(hist.Integral()))

def makeBinHisto(ydict):

    nbins = len(ydict)

    hist = TH1F("hyields","bin yields",nbins,-0.5,nbins+0.5)

    for idx,bin in enumerate(sorted(ydict.keys())):

        (yd,yerr) = ydict[bin]

        hist.SetBinContent(idx+1,yd)
        hist.SetBinError(idx+1,yerr)
        hist.GetXaxis().SetBinLabel(idx+1,bin)

    hist.Draw("histe")
    a = raw_input("wait")

def readFiles(fileList):

    binDict = {}

    for fname in fileList:
        binname = os.path.basename(fname)
        binname = binname.replace('.yields.root','')

        print 'Bin', binname, 'in file', fname

        tfile = TFile(fname,"READ")
        (yd,yerr) = getYield(tfile)

        print "Signal yield:", yd, "+/-", yerr
        tfile.Close()

        binDict[binname] = (yd,yerr)

    makeBinHisto(binDict)

if __name__ == "__main__":

    ## remove '-b' option
    _batchMode = False

    if '-b' in sys.argv:
        sys.argv.remove('-b')
        _batchMode = True

    if len(sys.argv) > 1:
        pattern = sys.argv[1]
        print '# pattern is', pattern
    else:
        print "No pattern given!"
        exit(0)

    #tfile  = TFile(fileName, "READ")
    #indir = os.path.dirname(fileName)

    # find files matching pattern
    fileList = glob.glob(pattern+"*.root")

    readFiles(fileList)
    #print fileList

    print 'Finished'
