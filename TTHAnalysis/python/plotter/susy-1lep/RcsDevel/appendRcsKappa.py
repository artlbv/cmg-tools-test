#!/usr/bin/env python
#import re, sys, os, os.path

import glob, os, sys
from math import hypot, sqrt
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

def getPredHist(tfile, hname):

    hRcsMB = tfile.Get("Rcs_SB/"+hname)

    if 'data' in hname:
        # use EWK template
        hKappa = tfile.Get("Kappa/EWK")
    else:
        hKappa = tfile.Get("Kappa/"+hname)

    # get yield from CR of MB
    hCR_MB = tfile.Get("CR_MB/"+hname)

    hPred = hCR_MB.Clone(hCR_MB.GetName()+"_pred")
    hPred.SetTitle("Predicted yield")

    hPred.Multiply(hRcsMB)
    hPred.Multiply(hKappa)

    return hPred

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

        # take anti/selected yields for Electrons
        ySeleEle = hOrig.GetBinContent(3,2); ySeleEleErr = hOrig.GetBinError(3,2);
        yAnti = hOrig.GetBinContent(3,1); yAntiErr = hOrig.GetBinError(3,1);

        yQCDFromAnti = fRatio*yAnti
        ySeleEleMinusAnti = ySeleEle - fRatio*yAnti# if ySeleEle > fRatio*yAnti else 0

        # error
        ySeleEleMinusAntiErr = sqrt(ySeleEleErr**2 + (yAntiErr*fRatio)**2 + (yAnti*fRatioErr)**2)

        # Set bin for electrons
        hCorr.SetBinContent(3,2,ySeleEleMinusAnti)
        hCorr.SetBinError(3,2,ySeleEleMinusAntiErr)

        ## Apply correction on combined electrons
        ySeleLep = hOrig.GetBinContent(2,2)
        ySeleMu = hOrig.GetBinContent(1,2); ySeleMuErr = hOrig.GetBinError(1,2)

        ySeleLepMinusAnti = ySeleMu + ySeleEleMinusAnti
        ySeleLepMinusAntiErr = hypot(ySeleMuErr,ySeleEleMinusAntiErr)

        # Set bin for combined leptons
        hCorr.SetBinContent(2,2,ySeleLepMinusAnti)
        hCorr.SetBinError(2,2,ySeleLepMinusAntiErr)

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
'''

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
                if not hNew:
                    print 'Could not create new histo for', pname
                else:
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

def makePredictHists(fileList):

    # get process names from file
    pnames = getPnames(fileList[0],'SR_MB')

    print 'Found these hists:', pnames

    #bindirs =  ['SR_MB','CR_MB','SR_SB','CR_SB']

    for fname in fileList:
        tfile = TFile(fname,"UPDATE")

        # create Rcs/Kappa dir struct
        if not tfile.GetDirectory("SR_MB_predict"):
            tfile.mkdir("SR_MB_predict")

            for pname in pnames:

                hPredict = getPredHist(tfile,pname)

                if hPredict:
                    tfile.cd("SR_MB_predict")
                    hPredict.Write()
                    #print "Wrote prediction of", pname
                else:
                    print "Failed to make prediction for", pname
        else:
            pass

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
    makePredictHists(fileList)

    #tfile = TFile(fileList[0],"UPDATE")
    #getQCDsubtrHisto(tfile,"background","")

    print 'Finished'
