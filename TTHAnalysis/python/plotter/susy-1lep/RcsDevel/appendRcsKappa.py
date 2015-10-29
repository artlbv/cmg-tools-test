#!/usr/bin/env python
#import re, sys, os, os.path

import glob, os, sys
from math import hypot
from ROOT import *

from readYields import getYield

def getPnames(fname,tdir):

    tfile = TFile(fname,"READ")
    tfile.cd(tdir)

    pnames = []

    for key in gDirectory.GetListOfKeys():

        obj = key.ReadObj()
        pnames.append(obj.GetName())

    tfile.Close()

    return pnames

def getRcsHist(tfile, hname, band = "SB"):

    hSR = tfile.Get("SR_"+band+"/"+hname)
    hCR = tfile.Get("CR_"+band+"/"+hname)

    hRcs = hSR.Clone(hSR.GetName().replace('x_','Rcs_'))
    hRcs.Divide(hCR)

    hRcs.GetYaxis().SetTitle("Rcs")

    return hRcs

def readQCDratios(fname = "lp_LTbins_NJ34_f-ratios_MC.txt"):

    fDict = {}

    with open(fname) as ftxt:
        lines = ftxt.readlines()

        for line in lines:
            if line[0] != '#':
                (bin,rat,err) = line.split()
                bin = bin.replace("_NJ34","")
                if 'LT' in bin:
                    fDict[bin] = (float(rat),float(err))

    #print 'Loaded f-ratios from file', fname
    #print fDict

    return fDict

def getQCDsubtrHisto(tfile, pname = "background", band = "CR_MB/", isMC = True, lep = "ele"):

    fRatio = 0.3 # default
    fRatioErr = 0.01 # default

    fRatios = {}

    if isMC: fRatios = readQCDratios("lp_LTbins_NJ34_f-ratios_MC.txt")
    else: fRatios = readQCDratios("lp_LTbins_NJ34_f-ratios_Data.txt")

    # get bin from filename
    for key in fRatios:
        if key in tfile.GetName():
            (fRatio,fRatioErr) = fRatios[key]
            #print "Found matching ratios for key" , key
            break
        #else: print "No corresp fRatio found! Using default."

    if lep == "ele" :

        hOrig = tfile.Get(band+pname) # original histogram
        if not hOrig: return 0

        hCorr = hOrig.Clone(pname+"_QCDsubtr") # histo to subtract QCD

        # take anti/selected ele yields
        ySele = hOrig.GetBinContent(3,2); ySeleLep = hOrig.GetBinContent(2,2)
        yAnti = hOrig.GetBinContent(3,1)

        #ySeleFromAnti = fRatio*yAnti
        ySeleMinusAnti = ySele - fRatio*yAnti if ySele > fRatio*yAnti else 0
        ySeleLepMinusAnti = ySeleLep - fRatio*yAnti if ySeleLep > fRatio*yAnti else 0

        hCorr.SetBinContent(3,2,ySeleMinusAnti)
        hCorr.SetBinContent(2,2,ySeleLepMinusAnti)

        # error -- FIXME
        if yAnti == 0: pass
        ySeleMinusAntiErr = ySeleMinusAnti*hypot(ySele,fRatio*yAnti)
        #hCorr.SetBinError(3,2,ySeleMinusAntiErr)

        ## return corrected histogram
        #hCorr.Write()
        return hCorr
    '''
    if True:
        hname = "x_QCD"
        yQCDanti = getYield(tfile,hname,"CR_"+band+"/", (lep,"anti"))

        pQCDsel = yQCDanti[0] * fRatio

        if yQCDanti[0] > 0:
            pQCDselErr = pQCDsel*hypot(yQCDanti[1]/yQCDanti[0],fRatioErr/fRatio)
        else:
            pQCDselErr = 0

        # closure
        yQCDsel = getYield(tfile,hname,"CR_"+band+"/", (lep,"sele"))
        print 'Expected nQCDsele = %f +- %f, predicted: %f +- %f' %(yQCDsel[0],yQCDsel[1],pQCDsel,pQCDselErr)

        return 1
    else:
        print "QCD estimate not yet implemented for muons"
        return 0
    '''


def getRcsWqcd(tfile, pname, band = "MB", lep = "lep"):

    rcsName = "Rcs_" + pname

    ySR = getYield(tfile,rcsName,"Rcs_"+band+"/", (lep,"sel"))
    yCR = getYield(tfile,rcsName,"Rcs_"+band+"/", (lep,"sel"))
    yCRanti = getYield(tfile,rcsName,"CR_"+band+"/", (lep,"anti"))

    kName = "Kappa_" + pname

    kappa = getYield(tfile,kName,"Kappa_"+band+"/", (lep,"sel"))


    ## Need 5 yields for RCS prediction
    # * SB SR: sele
    # * SB CR: sele & anti
    # * CR: sele & anti
    ## QCD:

    ## Prediction
    # SR = (CR-CRqcd) * SB_SR/(SB_CR-SB_CRqcd) * kappa


    return 1


def makeQCDsubtraction(fileList):

    # define hists to make QCD estimation
    pnames = ["background","data","QCD"] # process name
    #pnames = ["background","QCD"] # process name

    #pnames = getPnames(fileList[0],'SR_MB') # get process names from file
    #print 'Found these hists:', pnames

    bindirs =  ['SR_MB','CR_MB','SR_SB','CR_SB']

    for fname in fileList:
        tfile = TFile(fname,"UPDATE")

        for pname in pnames:
            for bindir in bindirs:

                if 'data' in pname: isMC = False
                else: isMC = True

                hNew = getQCDsubtrHisto(tfile,pname,bindir+"/",isMC)

                tfile.cd(bindir)
                hNew.Write()
                tfile.cd()

        tfile.Close()

def makeKappaHists(fileList):

    # filter
    #fileList = [fname for fname in fileList if 'NB3' not in fname]

    pnames = ["x_background","x_EWK"] # process name
    pnames = getPnames(fileList[0],'SR_MB') # get process names from file

    print 'Found these hists:', pnames

    bindirs =  ['SR_MB','CR_MB','SR_SB','CR_SB']
    #print bindirs

    for fname in fileList:
        tfile = TFile(fname,"UPDATE")

        #getQCDpred(tfile, 'MB')

        # create Rcs/Kappa dir struct
        if not tfile.GetDirectory("Rcs_MB"):
            tfile.mkdir("Rcs_MB")
            tfile.mkdir("Rcs_SB")
            tfile.mkdir("Kappa")

            for pname in pnames:

                hRcsMB = getRcsHist(tfile, pname, 'MB')
                hRcsSB = getRcsHist(tfile, pname, 'SB')

                # make kappa
                hKappa = hRcsMB.Clone(hRcsMB.GetName().replace('Rcs','Kappa'))
                hKappa.Divide(hRcsSB)

                hKappa.GetYaxis().SetTitle("Kappa")

                tfile.cd("Rcs_MB")
                hRcsMB.Write()

                tfile.cd("Rcs_SB")
                hRcsSB.Write()

                tfile.cd("Kappa")
                hKappa.Write()

        else:
            pass
            #print 'Already found Rcs and Kappa'

            '''
            yList = []
            print 'Yields for', pname
            for bindir in bindirs:
                yList.append(getYield(tfile,pname,bindir))

            print yList
            '''

        tfile.Close()

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

    makeQCDsubtraction(fileList)
    makeKappaHists(fileList)

    #tfile = TFile(fileList[0],"UPDATE")
    #getQCDsubtrHisto(tfile,"background","")

    print 'Finished'
