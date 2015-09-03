#!/usr/bin/env python
#import re, sys, os, os.path

import glob, os, sys
from math import hypot
from ROOT import *


def getYield(tfile, hname = "x_background",bindir = "", ytype = ('lep','sele')):

    if bindir != '': bindir += "/"

    hist = tfile.Get(bindir+hname)

    if hist.GetNbinsX() == 1:
        return (hist.GetBinContent(1),hist.GetBinError(1))

    elif hist.GetNbinsX() == 2 and hist.GetNbinsY() == 2:

        if ytype == ('mu','anti'):
            return (hist.GetBinContent(1,1),hist.GetBinError(1,1))
        elif ytype == ('mu','sele'):
            return (hist.GetBinContent(1,2),hist.GetBinError(1,2))
        elif ytype == ('ele','anti'):
            return (hist.GetBinContent(2,1),hist.GetBinError(2,1))
        elif ytype == ('ele','sele'):
            return (hist.GetBinContent(2,2),hist.GetBinError(2,2))
        elif ytype == ('lep','anti'):
            return (hist.GetBinContent(1,1)+hist.GetBinContent(1,2),hypot(hist.GetBinError(1,1),hist.GetBinError(1,2)))
        elif ytype == ('lep','sele'):
            return (hist.GetBinContent(2,1)+hist.GetBinContent(2,2),hypot(hist.GetBinError(2,1),hist.GetBinError(2,2)))
    else:
        return (hist.Integral(),TMath.sqrt(hist.Integral()))

def makeBinHisto(ydict, hname = "hYields"):

    nbins = len(ydict)

    hist = TH1F(hname,"bin yields for "+hname,nbins,-0.5,nbins+0.5)

    binList = [name for (name,yd,yerr) in ydict]

    #for idx,bin in enumerate(sorted(ydict.keys())):
    for idx,bin in enumerate(sorted(binList)):

        #(yd,yerr) = ydict[bin]
        (name,yd,yerr) = ydict[idx]

        hist.SetBinContent(idx+1,yd)
        hist.SetBinError(idx+1,yerr)

        binlabel = bin.replace('_SR','')
        binlabel = binlabel.replace('_CR','')
        binlabel = binlabel.replace('_CR','')
        binlabel = binlabel.replace('_NJ45','')
        binlabel = binlabel.replace('_NJ68','')

        hist.GetXaxis().SetBinLabel(idx+1,binlabel)

    return hist

def getYHisto(fileList, hname, hyname = "x_background"):

    #hyname = "x_T1tttt_HM_1200_800"

    binDict = {}
    binList = []

    for fname in fileList:
        binname = os.path.basename(fname)
        #binname = binname.replace('.yields.root','')
        binname = binname[:binname.find('.')]

        #makeRCS(binname)

        print 'Bin', binname, #'in file', fname

        tfile = TFile(fname,"READ")
        (yd,yerr) = getYield(tfile,hyname)

        print "yield:", yd, "+/-", yerr
        tfile.Close()

        binDict[binname] = (yd,yerr)
        binList.append((binname, yd, yerr))

    return makeBinHisto(binList, hname)

def matchSB(bname):

    name = bname+'_'

    if 'NJ68' in name:
        # match for NJ68
        name = name.replace('NJ68','NJ45')
        name = name.replace('NB2_','NB2i_')
        name = name.replace('NB3i_','NB2i_')
    elif 'NJ9' in name:
        # match for NJ9i
        name = name.replace('NB3i_','NB2i_')


    return name[:-1] #to remove the trailing _

def makeRCS(binname):

    # have to supply SR binname:
    # LTx_HTx_NBx_NJx_SR

    ## Need 5 yields for RCS
    # * SB SR: sele
    # * SB CR: sele & anti
    # * CR: sele & anti
    ## QCD:

    ## Prediction
    # SR = (CR-CRqcd) * SB_SR/(SB_CR-SB_CRqcd) * kappa

    # find bin names
    if '.' in binname:
        binname = binname[:binname.find('.')]
    purebname = binname[:binname.find('_NJ')]

    SRname = binname
    CRname = binname.replace('_SR','_CR')

    print 'replace', purebname, 'to', matchSB(purebname)

    SBname = matchSB(purebname) + '_NJ45'
    SR_SBname = SBname + '_SR'
    CR_SBname = SBname + '_CR'

    ## collect files
    print 'Found these bins matching to', binname
    print 'SR:', SRname
    print 'CR:', CRname
    print 'SR of SB:', SR_SBname
    print 'CR of SB:', CR_SBname

def makeRCShist(fileList, hname):

    # sort SR/CR files
    srList = [fname for fname in fileList if 'SR' in fname]
    crList = [fname for fname in fileList if 'CR' in fname]

    #print 'SR files:', srList
    #print 'CR files:', crList
    print 'Found %i SR files and %i CR files matching pattern' %(len(srList), len(crList))

    hSR = getYHisto(srList,"hSR"+hname)
    hCR = getYHisto(crList,"hCR"+hname)

    print hSR.GetNbinsX(), hCR.GetNbinsX()

    hRcs = hSR.Clone("hRcs")
    hRcs.Divide(hCR)

    hRcs.Draw("histe")
    a = raw_input("wait")

    return hRcs

def rename(nameList):

    newList = []

    for name in nameList:

        name = name.replace('NJ68','NJ45')
        name = name.replace('NB2_','NB2i_')
        name = name.replace('NB3i_','NB2i_')

        newList.append(name)

    return newList

def makeKappaHists(fileList):

    # filter
    #fileList = [fname for fname in fileList if 'NB3' not in fname]

    # split lists
    #nj45List = [fname for fname in fileList if 'NJ45' in fname]
    nj68List = [fname for fname in fileList if 'NJ68' in fname]
    nj45List = rename(nj68List)

    #print len(nj68List)
    #print rename(nj68List)
    #print len(nj45List)
    #print len(nj45List)

    hRcsNj68 = makeRCShist(nj68List,"_Nj68")
    hRcsNj68.SetLineColor(kBlue)
    hRcsNj68.SetMarkerStyle(22)
    hRcsNj68.SetMarkerColor(kBlue)

    hRcsNj45 = makeRCShist(nj45List,"_Nj45")
    hRcsNj45.SetLineColor(kRed)
    hRcsNj45.SetMarkerStyle(22)
    hRcsNj45.SetMarkerColor(kRed)

    hRcsNj68.Draw("histe1")
    hRcsNj45.Draw("histe1same")

    b = raw_input("cont")

    hKappa = hRcsNj68.Clone("hKappa")
    hKappa.Divide(hRcsNj45)
    hKappa.GetYaxis().SetRangeUser(0,2)

    hKappa.Draw("histe1")
    b = raw_input("cont")

    return 1


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

    # find files matching pattern
    fileList = glob.glob(pattern+"*.root")

    makeKappaHists(fileList)

    print 'Finished'
