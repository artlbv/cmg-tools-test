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

## Global vars
colorList = [1,2,4,7,9,8,3,6] + range(10,50)
_histStore = {}

_batchMode = False

colorDict = {'TT': kBlue-4,'TTdiLep':kBlue-4,'TTsemiLep':kBlue-2,'WJets':kGreen-2,
'QCD':kCyan-6,'SingleT':kViolet+5,'DY':kRed-6,'TTV':kOrange-3,'data':1,'background':2,'EWK':3}

def getSampColor(name):

    for samp in sorted(colorDict.keys()):
        if samp == name:
            return colorDict[samp]

    for samp in sorted(colorDict.keys()):
        if samp in name:
            return colorDict[samp]

    else: return 1

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
        #binLabel = binLabel.replace("_NJ68","")
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

    # Style
    col = getSampColor(hist.GetName())
    # col = colorList[i]
    #print "color for %s  %i" %(hist.GetName(),col)

    if "data" not in hist.GetName():
        if _batchMode == True:
            hist.SetFillColorAlpha(col,0.35)
        else:
            hist.SetFillColor(col)
            hist.SetFillStyle(3001)

    hist.SetLineColor(col)
    hist.SetMarkerColor(col)
    hist.SetMarkerStyle(20)

    if "Kappa" in cat:
        hist.GetYaxis().SetRangeUser(-0.05,0.3)

    if "Kappa" not in cat or "Rcs" not in cat:
        hist.GetYaxis().SetTitle("Events")

    return hist

def makeSampHists(yds,samps):

    histList = []

    for samp,cat in samps:

        yd = yds.getSampDict(samp,cat)
        hist = makeSampHisto(yd,samp,cat)

        histList.append(hist)

    return histList

def getRatio(histA,histB):

    ratio = histA.Clone("ratio_"+histA.GetName()+"_"+histB.GetName())
    ratio.Divide(histB)

    #ratio.GetYaxis().SetTitle("Ratio")
    ratio.GetYaxis().SetTitle(histA.GetTitle()+"/"+histB.GetTitle())
    ratio.GetYaxis().CenterTitle()

    ratio.SetLineColor(1)
    ratio.SetFillColor(0)
    ratio.SetFillStyle(0)

    return ratio

def getStack(histList):

    stack = THStack("stack","stack")

    for i,hist in enumerate(histList):
        stack.Add(hist)

        #style
        if _batchMode == True:
            hist.SetFillColorAlpha(hist.GetFillColor(),0.35)
        else:
            hist.SetFillStyle(3000)

    # Options
    #stack.Draw("GOFF") # GOFF doesn't actually draw anything
    #stack.GetXaxis().LabelsOption("v")

    return stack

def getTotal(histList):

    total = histList[0].Clone("total")
    total.Reset()

    for hist in histList:  total.Add(hist)

    total.SetTitle("Total")
    total.SetLineColor(1)
    total.SetFillColor(0)

    return total

def plotHists(histList, ratio = None):

    canv = TCanvas("canv","canv",800,600)

    if ratio != None:
        canv.SetWindowSize(600 + (600 - canv.GetWw()), (750 + (750 - canv.GetWh())));
        p1 = TPad("pad1","pad1",0,0.31,1,1);
        p1.SetBottomMargin(0);
        p1.Draw();
        p2 = TPad("pad2","pad2",0,0,1,0.31);
        p2.SetTopMargin(0);
        p2.SetBottomMargin(0.3);
        p2.SetFillStyle(0);
        p2.Draw();
        p1.cd();

    plotOpt = ""

    for i,hist in enumerate(histList):

        if  hist.ClassName() == 'THStack':
            hist.Draw("HIST")
            hist.GetXaxis().LabelsOption("v")
        elif "data" in hist.GetName():
            hist.Draw(plotOpt+"pE1")
        else:
            hist.Draw(plotOpt+"pE2")

        if "same" not in plotOpt: plotOpt += "same"

    canv.BuildLegend()

    if ratio != None:
        p2.cd()

        ratio.Draw()
        ratio.GetYaxis().SetRangeUser(0.,1.5)

        # 1 - line
        #xmin = ratio.GetXaxis().
        line = TLine(0,1,ratio.GetNbinsX(),1)
        line.SetLineWidth(1)
        line.Draw()
        SetOwnership(line,0)

    return canv

if __name__ == "__main__":

    ## remove '-b' option
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

    yds.addFromFiles(pattern,("lep","sele"))

    yds.showStats()


    samps = [
        ("QCD","CR_SB"),
        ("QCD_QCDpred","CR_SB"),
        ("QCD_QCDsubtr","CR_SB"),
        ]

    yds.printMixBins(samps)
    '''
    #ydQCD = yds.getSampDict("QCD","CR_SB")
    #hist = makeSampHisto(ydQCD,"QCD_CRSB")

    #yd = yds.getSampDict("EWK","CR_SB")
    #hist = makeSampHisto(yd,"h")

    samps = [
        ("background_QCDsubtr","CR_SB"),
        ("EWK","CR_SB"),
        ("data_QCDsubtr","CR_SB"),
        ]

    yds.printMixBins(samps)

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

    '''

    cat = "CR_SB"

    #mcSamps = [samp for samp in yds.samples if ("backgr" not in samp or "data" not in samp or "EWK" not in samp)]
    mcSamps = ['TT', 'SingleT', 'WJets', 'DY', 'QCD','TTV']
    print mcSamps

    samps = [(samp,cat) for samp in mcSamps]
    #add ewk
    #samps["EWK"] = cat

    print samps

    hists = makeSampHists(yds,samps)
    stack = getStack(hists)
    total = getTotal(hists)

    # Totals
    tots = [("background",cat),("data",cat)]

    hTot = makeSampHists(yds,tots)

    #stack.Draw("HIST")
    #canv = plotHists([stack,total]+hTot)
    #canv = plotHists([stack]+hTot)

    ratio = getRatio(hTot[1],total)

    canv = plotHists([stack]+hTot,ratio)

    #canv = plotHists([ratio])

    canv.SaveAs(canv.GetName()+".pdf")
    #hist.Draw("p")

    if not _batchMode: raw_input("Enter any key to exit")

