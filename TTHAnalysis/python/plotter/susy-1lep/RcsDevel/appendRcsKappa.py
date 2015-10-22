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


def getQCDpred(tfile, band = "MB", lep = "ele"):

    fRatio = 0.3 # FIXME
    fRatioErr = 0.01 # FIXME

    if lep == "ele" :

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

    else:
        return 0



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

    makeKappaHists(fileList)

    print 'Finished'
