#!/usr/bin/env python
import sys

from yieldClass import *
from ROOT import *

## ROOT STYLE
gStyle.SetOptTitle(0)
gStyle.SetOptStat(0)
gStyle.SetPadTopMargin(0.05)
gStyle.SetPadRightMargin(0.075)
gStyle.SetPadBottomMargin(0.225)

colorList = [1,2,4,7,9,8,3,6] + range(10,50)

_histStore = {}

def makeSampHisto(ydict, samp, cat):

    # create histo
    binList = sorted(ydict.keys())
    nbins = len(binList)

    hname = samp + "_" + cat
    if "Rcs" in cat:
        htitle = cat.replace("Rcs_","R_{CS}^{") + "} (%s)" %samp
    else:
        htitle = cat + " (%s)" %samp

    #hist = TH1F(hname,hname,nbins,-0.5,nbins+0.5)
    hist = TH1F(hname,htitle,nbins,0,nbins)

    # fill histo
    for ibin,bin in enumerate(binList):

        binLabel = bin
        binLabel = binLabel.replace("_NJ68","")
        binLabel = binLabel.replace("_",",")

        hist.GetXaxis().SetBinLabel(ibin+1,binLabel)

        if "Kappa" not in cat:
            hist.SetBinContent(ibin+1,ydict[bin].val)
            hist.SetBinError(ibin+1,ydict[bin].err)
        else:
            val = (ydict[bin].val-1)/10
            err = (ydict[bin].err)/10

            hist.SetBinContent(ibin+1,val)
            hist.SetBinError(ibin+1,err)

    # options
    hist.GetXaxis().LabelsOption("v")
    hist.GetYaxis().SetTitle(cat)

    if "Kappa" in cat:
        hist.GetYaxis().SetRangeUser(-0.05,0.3)

    return hist

def makeSampHists(samps):

    histList = []

    for samp,cat in samps:

        yd = yds.getSampDict(samp,cat)
        hist = makeSampHisto(yd,samp,cat)

        histList.append(hist)

    return histList

def plotHists(histList):

    canv = TCanvas("canv","canv",800,600)

    plotOpt = "pE3"

    for i,hist in enumerate(histList):

        # style
        hist.SetFillColorAlpha(colorList[i],0.35)
        hist.SetLineColor(colorList[i])
        hist.SetMarkerColor(colorList[i])
        hist.SetMarkerStyle(20)

        hist.Draw(plotOpt)

        if "same" not in plotOpt: plotOpt += "same"

    canv.BuildLegend()
    return canv

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

    '''
    # append / if pattern is a dir
    if os.path.isdir(pattern): pattern += "/"

    # find files matching pattern
    fileList = glob.glob(pattern+"*.root")
    '''

    ## Create Yield Storage
    yds = YieldStore("lepYields")

    yds.addFromFiles(pattern)

    yds.showStats()

    samps = [
        ("QCD","CR_SB"),
        ("QCD_QCDpred","CR_SB"),
        ("QCD_QCDsubtr","CR_SB"),
        ]

    #yds.printMixBins(samps)

    #ydQCD = yds.getSampDict("QCD","CR_SB")
    #hist = makeSampHisto(ydQCD,"QCD_CRSB")

    #yd = yds.getSampDict("EWK","CR_SB")
    #hist = makeSampHisto(yd,"h")

    '''
    samps = [
        ("background_QCDsubtr","CR_SB"),
        ("EWK","CR_SB"),
        ("data_QCDsubtr","CR_SB"),
        ]

    yds.printMixBins(samps)
    '''

    samps = [
        ("background","CR_SB"),
        ("background_QCDsubtr","CR_SB"),
        ("EWK","CR_SB"),
        #("data_QCDsubtr","CR_SB"),
        ]

    samps = [
        ("EWK","Kappa"),
        ("EWK","Rcs_SB"),
        ("EWK","Rcs_MB"),
        ]


    hists = makeSampHists(samps)
    canv = plotHists(hists)

    canv.SaveAs("canv.pdf")
    #hist.Draw("p")

    if not _batchMode: raw_input("Enter any key to exit")
