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
_alpha = 0.35
colorList = [2,4,7,9,8,3,6] + range(10,50)
_histStore = {}

_batchMode = False

colorDict = {'TT': kBlue-4,'TTdiLep':kBlue-4,'TTsemiLep':kBlue-2,'WJets':kGreen-2,
'QCD':kCyan-6,'SingleT':kViolet+5,'DY':kRed-6,'TTV':kOrange-3,'data':1,'background':2,'EWK':3}

def doLegend():

    leg = TLegend(0.63,0.525,0.87,0.875)
    leg.SetBorderSize(1)
    leg.SetTextFont(62)
    leg.SetTextSize(0.03321678)
    leg.SetLineColor(1)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(1001)

    return leg

def getSampColor(name):

    for samp in sorted(colorDict.keys()):
        if samp == name:
            return colorDict[samp]

    for samp in sorted(colorDict.keys()):
        if samp in name:
            return colorDict[samp]

    else: return 1

def prepKappaHist(hist):
    # prepare hist to be kappa

    hist.GetYaxis().SetNdivisions(505)
    hist.GetYaxis().SetTitle("#kappa")
    hist.GetYaxis().CenterTitle()
    hist.GetYaxis().SetTitleSize(0.1)
    hist.GetYaxis().SetTitleOffset(0.2)

    hist.GetYaxis().SetLabelSize(0.1)
    hist.GetYaxis().SetRangeUser(0.05,1.95)

    hist.GetXaxis().SetLabelSize(0.1)

def makeSampHisto(ydict, samp, cat, ind = 0):

    # create histo
    binList = sorted(ydict.keys())
    nbins = len(binList)

    hname = samp + "_" + cat
    if "Rcs" in cat:
        htitle = cat.replace("Rcs_","R_{CS}^{") + "} (%s)" %samp
    else:
        #htitle = cat + " (%s)" %samp
        htitle = "%s" %samp

    #hist = TH1F(hname,hname,nbins,-0.5,nbins+0.5)
    hist = TH1F(hname,htitle,nbins,0,nbins)

    # fill histo
    for ibin,bin in enumerate(binList):

        binLabel = bin
        binLabel = binLabel.replace("_NJ68","")
        binLabel = binLabel.replace("_NJ9i","")
        #binLabel = binLabel.replace("_",",")

        newLabel = "#splitline"

        splitbins = binLabel.split("_")#[:2]
        nbins = len(splitbins)

        if nbins == 2:
            newLabel = "#splitline{%s}{%s}" %(splitbins[0],splitbins[1])
        elif nbins == 3:
            newLabel = "#splitline{%s}{#splitline{%s}{%s}}" %(splitbins[0],splitbins[1],splitbins[2])
        else:
            newLabel = binLabel
        '''
        for ch in binLabel.split("_")[:2]:
            newLabel += "{%s}" % ch
        print newLabel
        '''

        hist.GetXaxis().SetBinLabel(ibin+1,newLabel)

        hist.SetBinContent(ibin+1,ydict[bin].val)
        hist.SetBinError(ibin+1,ydict[bin].err)

    # options
    hist.GetXaxis().LabelsOption("h")

    # Style
    if ("Kappa" not in cat) and ("Rcs" not in cat):
        col = getSampColor(hist.GetName())
    else:
        col = colorList[ind]
    #print "color for %s  %i" %(hist.GetName(),col)

    if "data" not in hist.GetName():
        if _batchMode == True:
            hist.SetFillColorAlpha(col,_alpha)
        else:
            hist.SetFillColor(col)
            hist.SetFillStyle(1001)

    hist.SetLineColor(col)
    hist.SetMarkerColor(col)
    hist.SetMarkerStyle(20)

    if "Kappa" in cat:
        hist.GetYaxis().SetRangeUser(-0.05,0.3)
        hist.GetYaxis().SetTitle("Events")
    elif "Rcs" in cat:
        hist.GetYaxis().SetRangeUser(0.005,0.35)
        hist.GetYaxis().SetTitle("R_{CS}")
    else:
        hist.GetYaxis().SetTitle("Events")

    return hist

def makeSampHists(yds,samps):

    histList = []

    for ind,(samp,cat) in enumerate(samps):

        yd = yds.getSampDict(samp,cat)
        hist = makeSampHisto(yd,samp,cat, ind)

        histList.append(hist)

    return histList

def getRatio(histA,histB):

    ratio = histA.Clone("ratio_"+histA.GetName()+"_"+histB.GetName())
    ratio.Divide(histB)

    #ratio.GetYaxis().SetTitle("Ratio")
    ratio.GetYaxis().SetTitle(histA.GetTitle()+"/"+histB.GetTitle())
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetNdivisions(505)
    ratio.GetYaxis().SetTitleSize(0.1)
    ratio.GetYaxis().SetTitleOffset(0.3)

    ratio.GetYaxis().SetLabelSize(0.1)
    ratio.GetYaxis().SetRangeUser(0.05,1.95)

    ratio.GetXaxis().SetLabelSize(0.1)

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
            hist.SetFillStyle(1001)

    # Options
    #stack.Draw("GOFF") # GOFF doesn't actually draw anything
    #stack.GetXaxis().LabelsOption("v")

    return stack

def getTotal(histList):
    # to be used only for ratio and error band

    total = histList[0].Clone("total")
    total.Reset()
    total.SetTitle("total")
    total.SetName("total")

    for hist in histList:  total.Add(hist)

    total.SetLineColor(0)
    total.SetFillColor(kGray)
    total.SetFillStyle(3144)
    total.SetMarkerStyle(0)
    total.SetMarkerColor(0)

    return total

def plotHists(histList, ratio = None):

    canv = TCanvas("canv","canv",1000,600)
    leg = doLegend()

    if ratio != None:
        #canv.SetWindowSize(600 + (600 - canv.GetWw()), (750 + (750 - canv.GetWh())));
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
            hist.GetXaxis().LabelsOption("h")

            for h in hist.GetHists():
                leg.AddEntry(h,h.GetTitle(),"f")
        elif "data" in hist.GetName():
            hist.Draw(plotOpt+"pE1")
            leg.AddEntry(hist,hist.GetTitle(),"p")
        elif "total" in hist.GetName():
            hist.Draw(plotOpt+"E2")
            leg.AddEntry(hist,"MC Uncertainty","f")
        else:
            hist.Draw(plotOpt+"pE2")
            leg.AddEntry(hist,hist.GetTitle(),"pf")

        if "same" not in plotOpt: plotOpt += "same"

    #canv.BuildLegend()
    leg.Draw()
    SetOwnership(leg,0)

    if ratio != None:
        p2.cd()

        ratio.Draw()

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

    '''
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
    '''

    sampsRcs = [
        ("EWK","Rcs_SB"),
        ("EWK","Rcs_MB"),
        ]

    rcsHists = makeSampHists(yds,sampsRcs)
    hKappa = makeSampHists(yds,[("EWK","Kappa")])[0]

    prepKappaHist(hKappa)

    canv = plotHists(rcsHists,hKappa)

    '''
    cat = "CR_SB"

    #mcSamps = [samp for samp in yds.samples if ("backgr" not in samp or "data" not in samp or "EWK" not in samp)]
    mcSamps = ['DY','TTV','SingleT','WJets','TT','QCD']
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

    canv = plotHists([stack,total,hTot[1]],ratio)

    #canv = plotHists([ratio])

    #hist.Draw("p")
    '''

    canv.SaveAs(canv.GetName()+".pdf")
    if not _batchMode: raw_input("Enter any key to exit")
