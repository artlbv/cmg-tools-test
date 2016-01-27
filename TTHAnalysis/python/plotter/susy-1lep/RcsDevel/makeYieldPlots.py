#!/usr/bin/env python
import sys, math

from yieldClass import *
from ROOT import *

## ROOT STYLE
gStyle.SetOptTitle(0)
gStyle.SetOptStat(0)
gStyle.SetPadTopMargin(0.075)
gStyle.SetPadRightMargin(0.075)
gStyle.SetPadBottomMargin(0.25)
gStyle.SetLegendBorderSize(0)

## CMS LUMI
import CMS_lumi

CMS_lumi.writeExtraText = 1
CMS_lumi.extraText = "Preliminary"
iPos = 11
if( iPos==0 ): CMS_lumi.relPosX = 0.2


## Global vars
_alpha = 0.55
colorList = [2,4,7,9,8,3,6] + range(10,50)
_histStore = {}
_lines = []

_batchMode = True#False

colorDict = {'TTJets': kBlue-4,'TTdiLep':kBlue-4,'TTsemiLep':kBlue-2,'WJets':kGreen-2,
             'QCD':kCyan-6,'SingleT':kViolet+5,'DY':kRed-6,'TTV':kOrange-3,'data':1,'background':2,'EWK':3}

def doLegend(pos = "TM",nEntr = None):

    if pos == "TM":
        if nEntr:
            leg = TLegend(0.4,0.875-(nEntr*0.2),0.6,0.875)
        else:
            #leg = TLegend(0.4,0.5,0.6,0.85)
            leg = TLegend(0.3,0.5,0.45,0.85)
    elif pos == "Long":
        #leg = TLegend(0.2,0.75,0.85,0.85) # Top
        leg = TLegend(0.2,0.35,0.85,0.45) # Bottom

    leg.SetBorderSize(1)
    leg.SetTextFont(62)
    leg.SetTextSize(0.03321678)
    leg.SetLineColor(0)
    leg.SetLineStyle(0)
    leg.SetLineWidth(0)

    if _batchMode == False: leg.SetFillColor(0)
    else: leg.SetFillColorAlpha(0,_alpha)

    leg.SetFillStyle(1001)
    #leg.SetFillStyle(0)

    return leg

def getSampColor(name):

    if "TT_" in name: name = name.replace("TT_","TTJets_")

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

def getUniqLabels(labels):

    nbin = len(labels[0].split("_"))

    # Dict that counts labels
    binCnts = {n:set() for n in range(nbin)}

    # Count appearance of bins
    for lab in labels:
        labs = lab.split("_")
        for i in range(len(labs)):
            binCnts[i].add(labs[i])

    # Make labels with short names
    newLabs = {}
    for lab in labels:
        labs = lab.split("_")
        newlab = "_".join(bin for i,bin in enumerate(labs) if len(binCnts[i]) > 1)
        newLabs[lab] = newlab

    return newLabs

def getCleanLabel(binLabel):

    # standart replacements
    binLabel = binLabel.replace("_SR","")
    binLabel = binLabel.replace("_CR","")
    binLabel = binLabel.replace("f6","")
    binLabel = binLabel.replace("f9","")

    binLabel = binLabel.replace("LTi","")
    #binLabel = binLabel.replace("NB0","")
    #binLabel = binLabel.replace("NB2i","")

    #binLabel = binLabel.replace("_NJ68","")
    #binLabel = binLabel.replace("_NJ9i","")
    #binLabel = binLabel.replace("_",",")


    return binLabel

def makeSampHisto(yds, samp, cat, hname = "", ind = 0):

    # yield dict
    ydict = yds.getSampDict(samp,cat)

    if not ydict:
        print "Could not read dict", samp, cat
        return 0

    # create histo
    #binList = sorted(ydict.keys())
    binList = []
    # sort bins by NJ
    for njbin in ['NJ3','NJ4','NJ5','NJ6','NJ9']:
        binList += [b for b in sorted(ydict.keys()) if njbin in b]

    nbins = len(binList)

    if hname == "": hname = samp + "_" + cat
    if "Rcs" in cat:
        htitle = cat.replace("Rcs_","R_{CS}^{") + "} (%s)" %samp
    else:
        #htitle = cat + " (%s)" %samp
        htitle = "%s" %samp

    #hist = TH1F(hname,hname,nbins,-0.5,nbins+0.5)
    hist = TH1F(hname,htitle,nbins,0,nbins)

    # for bin labels
    labels = []
    for ibin,bin in enumerate(binList):
        label = ydict[bin].label if ydict[bin].label != "" else bin
        labels.append(getCleanLabel(label))

    ulabs = getUniqLabels(labels)

    # fill histo
    for ibin,bin in enumerate(binList):

        #binLabel = bin
        binLabel = ydict[bin].label
        if binLabel == "": binLabel = bin

        binLabel = getCleanLabel(binLabel)

       # if binLabel in ulabs: binLabel = ulabs[binLabel]

        newLabel = "#splitline"

        splitbins = binLabel.split("_")#[:2]
        nbins = len(splitbins)

        if nbins == 2:
            newLabel = "#splitline{%s}{%s}" %(splitbins[0],splitbins[1])
        elif nbins == 3:
            newLabel = "#splitline{%s}{#splitline{%s}{%s}}" %(splitbins[0],splitbins[1],splitbins[2])
        elif nbins == 4:
            newLabel = "#splitline{%s}{#splitline{%s}{#splitline{%s}{%s}}}" %(splitbins[0],splitbins[1],splitbins[2],splitbins[3])
        else:
            newLabel = binLabel

        hist.GetXaxis().SetBinLabel(ibin+1,newLabel)

        hist.SetBinContent(ibin+1,ydict[bin].val)
        hist.SetBinError(ibin+1,ydict[bin].err)

    # options
    hist.GetXaxis().LabelsOption("h")

    # Style
    if ("Kappa" not in cat) and ("Rcs" not in cat):
    #    col = getSampColor(hist.GetName())
        col = getSampColor(hist.GetName())
    else:
        col = getSampColor(hist.GetName())
    #    col = getSampColor(samp)
    #    col = colorList[ind]
    #print "color for %s  %i" %(hist.GetName(),col)

    if "data" not in hist.GetName():
        if _batchMode == True:
            hist.SetFillColorAlpha(col,_alpha)
        else:
            hist.SetFillColor(col)
            hist.SetFillStyle(3001)

    hist.SetLineColor(col)
    #hist.SetLineColor(1)
    hist.SetMarkerColor(col)
    hist.SetMarkerStyle(20)

    if "Kappa" in cat:
        #hist.GetYaxis().SetRangeUser(0.05,1.95)
        hist.GetYaxis().SetTitle("Kappa")
    elif "Rcs" in cat:
        #hist.GetYaxis().SetRangeUser(0.005,0.35)
        hist.GetYaxis().SetTitle("R_{CS}")
    else:
        hist.GetYaxis().SetTitle("Events")

    #SetOwnership(hist, 0)
    _histStore[hist.GetName()] = hist
    return hist

def makeSampHists(yds,samps):

    histList = []

    for ind,(samp,cat) in enumerate(samps):

        #yd = yds.getSampDict(samp,cat)
        #if yd:
        hist = makeSampHisto(yds,samp,cat,"",ind)

        histList.append(hist)

    return histList

def getMarks(hist):

    if hist.ClassName() == "THStack":
        hist = hist.GetHistogram()

    # line markers
    marks = []
    ltmark = 0

    for bin in range(1,hist.GetNbinsX()+1):
        # for vertical lines
        binLabel = hist.GetXaxis().GetBinLabel(bin).replace("#splitline{","")
        #print binLabel

        ltbin = binLabel.split("}")[0] # should be LT
        #print ltbin, ltmark
        if ltmark == 0: ltmark = ltbin
        elif ltmark != ltbin:
            ltmark = ltbin
            marks.append(bin)

    return marks

def prepRatio(hist, keepStyle = False):

    hist.GetYaxis().CenterTitle()
    hist.GetYaxis().SetNdivisions(505)
    hist.GetYaxis().SetTitleSize(0.08)
    hist.GetYaxis().SetTitleOffset(0.3)
    hist.GetYaxis().SetLabelSize(0.1)
    hist.GetYaxis().SetRangeUser(0.05,2.1)

    hist.GetXaxis().SetLabelSize(0.1)

    hist.SetFillColor(0)
    hist.SetFillStyle(0)

    if not keepStyle:
        hist.SetLineColor(1)
        hist.SetMarkerColor(1)

    return hist


def getRatio(histA,histB, keepStyle = False):

    ratio = histA.Clone("ratio_"+histA.GetName()+"_"+histB.GetName())
    ratio.Divide(histB)

    #ratio.GetYaxis().SetTitle("Ratio")
    title = "#frac{%s}{%s}" %(histA.GetTitle(),histB.GetTitle())
    ratio.GetYaxis().SetTitle(title)
    ratio.GetYaxis().CenterTitle()
    ratio.GetYaxis().SetNdivisions(505)
    ratio.GetYaxis().SetTitleSize(0.08)
    ratio.GetYaxis().SetTitleOffset(0.3)
    ratio.GetYaxis().SetLabelSize(0.1)

    ymax = min(2.9,1.3*ratio.GetMaximum())
    ymin = 0.8*min(ratio.GetMinimum(),0.85)
    ratio.GetYaxis().SetRangeUser(ymin,ymax)
    ratio.SetMaximum(ymax)
    ratio.SetMinimum(ymin)

    ratio.GetXaxis().SetLabelSize(0.1)

    if not keepStyle:
        ratio.SetLineColor(1)
        ratio.SetMarkerColor(1)
        ratio.SetMarkerStyle(20)
    ratio.SetFillColor(0)
    ratio.SetFillStyle(0)

    _histStore[ratio.GetName()] = ratio
    return ratio

def getPull(histA,histB):

    pull = histA.Clone("pull_"+histA.GetName()+"_"+histB.GetName())
    pull.Add(histB,-1)
    #pull.Divide(histB)

    for ibin in range(1,pull.GetNbinsX()+1):
        err = histB.GetBinError(ibin)
        if err > 0:
            pull.SetBinContent(ibin,pull.GetBinContent(ibin)/err)
            pull.SetBinError(ibin,pull.GetBinError(ibin)/err)
        else:
            pull.SetBinContent(ibin,0)
            pull.SetBinError(ibin,0)

    #pull.GetYaxis().SetTitle("Pull")
    #title = "#frac{%s - %s}{%s}" %(histA.GetTitle(),histB.GetTitle(),histB.GetTitle())
    #title = "#frac{%s - %s}{#sigma(%s)}" %(histA.GetTitle(),histB.GetTitle(),histA.GetTitle())
    title = "#frac{%s - %s}{#sigma(%s)}" %(histA.GetTitle(),histB.GetTitle(),histB.GetTitle())

    pull.GetYaxis().SetTitle(title)
    pull.GetYaxis().CenterTitle()
    pull.GetYaxis().SetNdivisions(505)
    pull.GetYaxis().SetTitleSize(0.1)
    pull.GetYaxis().SetTitleOffset(0.3)

    pull.GetYaxis().SetLabelSize(0.1)
    pull.GetYaxis().SetRangeUser(-5,5)

    pull.GetXaxis().SetLabelSize(0.1)

    pull.SetLineColor(1)
    #pull.SetMarkerColor(1)
    pull.SetFillColor(0)
    pull.SetFillStyle(0)

    return pull

def getStack(histList):

    stack = THStack("stack","stack")

    for i,hist in enumerate(histList):
        stack.Add(hist)

        #style
        if _batchMode == True:
            hist.SetFillColorAlpha(hist.GetFillColor(),_alpha)
        else:
            hist.SetFillStyle(1001)

    # Options
    #stack.Draw("GOFF") # GOFF doesn't actually draw anything
    #stack.GetXaxis().LabelsOption("v")

    return stack

def getSquaredSum(histList):

    sqHist = histList[0].Clone()

    for i,hist in enumerate(histList):
        if i > 0:
            for bin in range(1,hist.GetNbinsX()+1):
                x = sqHist.GetBinContent(bin)
                new = x*x + hist.GetBinContent(bin)*hist.GetBinContent(bin)
                sqHist.SetBinContent(bin, math.sqrt(new))
    sqHist.SetMarkerStyle(34)
    sqHist.SetMarkerSize(2)
    sqHist.SetMarkerColor(kBlack)
    sqHist.SetTitle("sqSum")
    sqHist.SetName("sqSum")
    return sqHist

def getHistWithError(hCentral, hSyst, new = True):
    if new:
        histWithError = hCentral.Clone()
        histWithError.SetFillColor(kBlue)
        histWithError.SetFillStyle(3002)
    else:
        histWithError = hCentral

    for bin in range(1,hCentral.GetNbinsX()+1):
        sys = hCentral.GetBinContent(bin)*hSyst.GetBinContent(bin)
        #err = math.sqrt(hCentral.GetBinError(bin)*hCentral.GetBinError(bin) + sys*sys)
        err = math.hypot(hCentral.GetBinError(bin),sys)
        histWithError.SetBinError(bin, err)

    return  histWithError



def getTotal(histList):
    # to be used only for ratio and error band

    total = histList[0].Clone("total")
    total.Reset()
    total.SetTitle("total")
    total.SetName("total")

    for hist in histList:  total.Add(hist)

    total.SetLineColor(0)
    total.SetFillColor(kGray)
    total.SetFillStyle(3244)
    total.SetMarkerStyle(0)
    total.SetMarkerColor(0)

    return total

def getCatLabel(name):

    cname = name
    cname = cname.replace("_"," ")
    cname = cname.replace("SB","N_{j} #in [4,5]")

    #cname = cname.replace("MB","N_{j} #in [6,8]")
    #cname = cname.replace("MB","N_{j} #geq 9")
    cname = cname.replace("MB predict X NJ5X","N_{j} = 5")
    cname = cname.replace("MB predict X NJ68X","N_{j} #in [6,8]")
    cname = cname.replace("MB predict X NJ9X","N_{j} #geq 9")
    #cname = cname.replace("MB","N_{j} == 5")

    return cname

def plotHists(cname, histList, ratio = None, legPos = "TM", width = 800, height = 600, logY = False):

    #canv = TCanvas(cname,cname,1400,600)
    canv = TCanvas(cname,cname,width,height)
    #leg = doLegend(len(histList)+1)
    leg = doLegend(legPos)
    if legPos == "Long":
        nh = 1
        for hist in histList:
            if hist.ClassName() == "THStack":
                nh += len(hist.GetHists())
            else:
                nh += 1
        leg.SetNColumns(nh)

    SetOwnership(canv, 0)
    SetOwnership(leg, 0)

    head = getCatLabel(cname)
    leg.SetHeader(head)

    if ratio != None:

        if type(ratio) == list:
            ratios = ratio
            ratio = ratios[0]
            multRatio = True
        else:
            multRatio = False

        #canv.SetWindowSize(600 + (600 - canv.GetWw()), (750 + (750 - canv.GetWh())));
        p2 = TPad("pad2","pad2",0,0,1,0.31);
        p2.SetTopMargin(0);
        p2.SetBottomMargin(0.31);
        p2.SetFillStyle(0);
        p2.Draw();

        p1 = TPad("pad1","pad1",0,0.31,1,1);
        p1.SetBottomMargin(0.02);
        p1.Draw();

        p2.cd()
        ratio.Draw("pe1")

        # 1 - line
        #xmin = ratio.GetXaxis().
        if "pull" in ratio.GetName():
            line = TLine(0,0,ratio.GetNbinsX(),0)
        elif "ratio" in ratio.GetName():
            line = TLine(0,1,ratio.GetNbinsX(),1)
        else:
            line = TLine(0,1,ratio.GetNbinsX(),1)

        line.SetLineWidth(1)
        line.Draw()
        SetOwnership(line,0)

        # plot bins separator
        marks = getMarks(ratio)
        # do vertical lines
        if len(marks) != 0:
            #print marks
            axis = ratio.GetXaxis()
            ymin = ratio.GetMinimum(); ymax = ratio.GetMaximum()
            #ymin = ratio.GetYaxis().GetXmin(); ymax = ratio.GetYaxis().GetXmax()
            for i,mark in enumerate(marks):
                pos = axis.GetBinLowEdge(mark)
                line = TLine(pos,ymin,pos,ymax)
                #line.SetName("line_mark_"+str(mark))
                line.SetLineStyle(3)
                if i == 3: line.SetLineStyle(2) # nj6 -> nj9
                line.Draw("same")
                _lines.append(line)

        if multRatio:
            for rat in ratios[1:]:
                rat.Draw("pe2same")

        p1.cd();
    else:
        canv.SetBottomMargin(0.1)

    plotOpt = ""

    # get Y-maximum/minimum
    ymax = max([h.GetMaximum() for h in histList])
#    ymin = min([h.GetMinimum() for h in histList]);

    for h in histList:
        if h.ClassName() == "THStack":
            extHistList = histList + [h for h in h.GetHists()]

    ymin = min([h.GetMinimum() for h in extHistList]);

    # for fractions set min to 0
    if not logY:
        if ymax < 1.01 and ymax >= 1: ymax == 1; ymin = 0
        else: ymax *= 1.5; ymin *= 0.8
    else:
        ymax *= 100; ymin = max(0.05,0.5*ymin)

    #ymin = 0
    #ymax = min(ymax, 1.5)

    # make dummy for stack
    if histList[0].ClassName() == "THStack":
        dummy = histList[0].GetHists()[0].Clone("dummy")
        dummy.Reset()
        # draw dymmy first
        _histStore[dummy.GetName()] = dummy
        histList = [dummy] + histList

    for i,hist in enumerate(histList):

        if not hist.ClassName() == 'THStack':

            hist.GetYaxis().SetTitleSize(0.05)
            hist.GetYaxis().SetTitleOffset(0.6)

            if ratio == None: hist.GetYaxis().SetLabelSize(0.4)
            else: hist.GetYaxis().SetLabelSize(0.05)

        # range
        hist.SetMaximum(ymax)
        hist.SetMinimum(ymin)
        #print hist.GetName()
        if "dummy" == hist.GetName():
            hist.Draw()
        elif  hist.ClassName() == 'THStack':
            #continue
            hist.Draw("HISTsame")
            hist.GetXaxis().LabelsOption("h")
            hist.GetYaxis().SetTitle("Events")
            hist.GetYaxis().SetTitleSize(0.1)
            hist.GetYaxis().SetTitleOffset(0.6)

            for h in reversed(hist.GetHists()):
                leg.AddEntry(h,h.GetTitle(),"f")
        elif ("data" in hist.GetName()) or ("Data" in hist.GetName()):
            hist.Draw(plotOpt+"pE1")
            leg.AddEntry(hist,hist.GetTitle(),"pl")
        elif "total" in hist.GetName():
            hist.Draw(plotOpt+"E2")
            leg.AddEntry(hist,"MC Uncertainty","f")
        elif "Syst" in hist.GetName():
            hist.Draw(plotOpt+"E2")
            leg.AddEntry(hist,hist.GetTitle(),"f")
        elif "pred" in hist.GetName():
            hist.Draw(plotOpt+"pE1")
            leg.AddEntry(hist,hist.GetTitle(),"pl")
        elif "sqSum" in hist.GetName():
            hist.Draw(plotOpt+"p")
            leg.AddEntry(hist,"Sum squared uncertainties","p")
        else:
            if len(histList) < 3:
                hist.Draw(plotOpt+"pE2")
                leg.AddEntry(hist,hist.GetTitle(),"pf")
            else:
                hist.Draw(plotOpt+"pE2")
                leg.AddEntry(hist,hist.GetTitle(),"pf")

        # remove axis label with ratio
        if i == 0 and ratio != None:
            hist.GetXaxis().SetLabelOffset(1)

        if i == 0:
            # do vertical lines
            marks = getMarks(hist)
            if len(marks) != 0:
                #print marks
                axis = hist.GetXaxis()
                for i,mark in enumerate(marks):
                    pos = axis.GetBinLowEdge(mark)
                    line = TLine(pos,ymin,pos,ymax)
                    #line.SetName("line_mark_"+str(mark))
                    line.SetLineStyle(3)
                    if i == 3: line.SetLineStyle(2) # nj6 -> nj9
                    line.Draw("same")
                    _lines.append(line)

        if "same" not in plotOpt: plotOpt += "same"

    #canv.BuildLegend()
    leg.Draw()
    SetOwnership(leg,0)

    if logY: p1.SetLogy()

    # draw CMS lumi
    if ratio != None:
        CMS_lumi.CMS_lumi(p1, 4, iPos)
    else:
        CMS_lumi.CMS_lumi(canv, 4, iPos)

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

    #BinMask LTX_HTX_NBX_NJX for canvas names
    basename = os.path.basename(pattern)
    mask = basename.replace("*","X_")

    ## Create Yield Storage
    yds = YieldStore("lepYields")

    yds.addFromFiles(pattern,("ele","anti"))

    yds.showStats()

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

    sampsRcs = [
    ("EWK","Rcs_SB"),
    ("EWK","Rcs_MB"),
    ]

    rcsHists = makeSampHists(yds,sampsRcs)
    hKappa = makeSampHists(yds,[("EWK","Kappa")])[0]


    prepKappaHist(hKappa)

    canv = plotHists("bla",rcsHists,hKappa)

    '''
    cat = "SR_MB"


    #mcSamps = [samp for samp in yds.samples if ("backgr" not in samp or "data" not in samp or "EWK" not in samp)]
    mcSamps = ['DY','TTV','SingleT','WJets','TT','QCD']
    #mcSamps = ['WJets','TT','QCD']
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
    #tots = [("background",cat),("background",cat)]

    hTot = makeSampHists(yds,tots)

    #stack.Draw("HIST")
    #canv = plotHists(cat,[stack,total]+hTot)
    #canv = plotHists(cat,[stack]+hTot)

    ratio = getRatio(hTot[1],total)

    canv = plotHists("AntiEle_"+cat,[stack,total,hTot[1]],ratio)
    #canv = plotHists("AntiEle_"+cat,[stack,total],ratio)

    #canv = plotHists(cat,[ratio])

    #hist.Draw("p")

    if not _batchMode: raw_input("Enter any key to exit")
    canv.SaveAs("BinPlots/"+mask+canv.GetName()+".pdf")
