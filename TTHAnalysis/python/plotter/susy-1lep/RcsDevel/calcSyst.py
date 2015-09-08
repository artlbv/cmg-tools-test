#!/usr/bin/env python
#import re, sys, os, os.path

import glob, os, sys
from math import hypot
from ROOT import *

from readYields import getYield

def getHnames(fname,tdir):

    tfile = TFile(fname,"READ")
    tfile.cd(tdir)

    hnames = []

    for key in gDirectory.GetListOfKeys():

        obj = key.ReadObj()
        hnames.append(obj.GetName())

    tfile.Close()

    return hnames

def getSystHist(tfile, hname, syst = "Xsec"):

    upName = hname + '_' + syst + '-Up'
    dnName = hname + '_' + syst + '-Down'

    #print tfile, hname, upName, dnName

    hNorm = tfile.Get(hname)
    hUp = tfile.Get(upName)
    hDown = tfile.Get(dnName)

    if not hUp or not hDown:
        print 'No systematics found!'
        return 1

    hSyst = hNorm.Clone(hNorm.GetName() + '_' + syst + '_syst')

    hPlus = hNorm.Clone(hNorm.GetName() + '_' + syst + '_plus')
    hPlus.Add(hUp,-1)

    hMinus = hNorm.Clone(hNorm.GetName() + '_' + syst + '_minus')
    hMinus.Add(hDown,-1)

    # find maximum deviations
    for xbin in range(1,hSyst.GetNbinsX()+1):
        for ybin in range(1,hSyst.GetNbinsY()+1):

            # reset bins
            hSyst.SetBinContent(xbin,ybin,0)
            hSyst.SetBinError(xbin,ybin,0)

            maxDev = 0
            maxErr = 0

            # fill maximum deviation
            if abs(hPlus.GetBinContent(xbin,ybin)) > abs(hMinus.GetBinContent(xbin,ybin)):
                maxDev = abs(hPlus.GetBinContent(xbin,ybin))
                #maxErr = abs(hPlus.GetBinError(xbin,ybin))
            else:
                maxDev = abs(hMinus.GetBinContent(xbin,ybin))
                #maxErr = abs(hMinus.GetBinError(xbin,ybin))

            if hNorm.GetBinContent(xbin,ybin) > 0:
                maxDev /= hNorm.GetBinContent(xbin,ybin)
                #maxErr = hypot(maxErr,hNorm.GetBinError(xbin,ybin))

            hSyst.SetBinContent(xbin,ybin,maxDev)
            hSyst.SetBinError(xbin,ybin,maxErr)

    return hSyst


def makeSystHists(fileList):

    # filter
    #fileList = [fname for fname in fileList if 'NB3' not in fname]

    hnames = ["T1tttt_Scan"] # process name
    #hnames = getHnames(fileList[0],'SR_MB') # get process names from file
    #print 'Found these hists:', hnames

    systNames = ["Xsec"]

    bindirs =  ['SR_MB','CR_MB','SR_SB','CR_SB']

    for fname in fileList:
        tfile = TFile(fname,"UPDATE")

        for bindir in bindirs:

            for hname in hnames:
                for syst in systNames:

                    hSyst = getSystHist(tfile, bindir+'/'+ hname, syst)
                    hSyst.Write()

            '''
            # create Syst folder structure
            if not tfile.GetDirectory(bindir+"/Syst"):
                tfile.mkdir(bindir+"/Syst")

                for hname in hnames:
                    for syst in systNames:

                        tfile.cd(bindir+"/Syst")
                        hSyst = getSystHist(tfile, bindir+'/'+ hname, syst)
                        hSyst.Write()
            else:
                print 'Already found syst'
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

    makeSystHists(fileList)

    print 'Finished'
