#!/usr/bin/python

import sys
import os
#sys.argv.append( '-b' )

from ROOT import *
from array import array

_canvStore = []
_histStore = {}
_hEffStore = {}

_fitrStore = []

_colorList = [2,3,4,6,7,8,9] + range(10,50)


def getLegend(pos = 'ne'):
    if pos == 'ne':
        leg = TLegend(0.4,0.7,0.9,0.9)
    elif pos == 'log':
        leg = TLegend(0.6,0.8,0.99,0.99)
    elif pos == 'roc':
        leg = TLegend(0.15,0.2,0.7,0.4)
    elif pos == 'fit':
        leg = TLegend(0.15,0.65,0.5,0.8)

    leg.SetBorderSize(1)
    leg.SetTextFont(62)
    leg.SetTextSize(0.03321678)
    leg.SetLineColor(1)
    leg.SetLineStyle(1)
    leg.SetLineWidth(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(1001)

    return leg

def turnon_func(x, par):

    halfpoint = par[0]
    #slope = max(par[1],0.00001)
    width = max(par[1],1)
    plateau = par[2]

    #offset = par[3]
    #plateau = 1.0
    offset = 0

    pt = TMath.Max(x[0],0.000001)

    arg = 0
    #print pt, halfpoint, width
    #arg = (pt - halfpoint)/(TMath.Sqrt(pt)*slope)
    arg = (pt - halfpoint) / (width * TMath.Sqrt(2))

    fitval = offset + plateau * 0.5 * (1 + TMath.Erf(arg))
    #fitval = offset + plateau * TMath.Erfc(arg)

    return fitval

def textBox():

    pt = TPaveText(.05,.1,.95,.8);

    pt.AddText("A TPaveText can contain severals line of text.");
    pt.AddText("They are added to the pave using the AddText method.");
    pt.AddLine(.0,.5,1.,.5);
    pt.AddText("Even complex TLatex formulas can be added:");
    pt.AddText("F(t) = #sum_{i=-#infty}^{#infty}A(i)cos#[]{#frac{i}{t+i}}");

    return pt


def cutsToString(cutList):

    cutstr = ''

    for i, cut in enumerate(cutList):
        cutstr += cut

        if i != len(cutList)-1: cutstr += ' && '

    return cutstr

def varBinSize():

    bins = '[10,15,20,50,80]'
    edges = [ float(f) for f in bins[1:-1].split(",") ]

    histo = ROOT.TH1F("dummy","dummy",len(edges)-1,array('f',edges))

    print edges

    return histo

def setColors(histList):

    #    colorList = [3,2,ROOT.kGreen-2,1]
    colorList = [1,2,3,4]

    for ind,hist in enumerate(histList):
        hist.SetLineColor(colorList[ind])
        hist.SetMarkerColor(colorList[ind])

def getHistsFromTree(tree, var = 'MET', refTrig = '', cuts = '', testTrig = '', maxEntries = -1):

    gStyle.SetOptStat(0)

    # maximum number of entries to process
    if maxEntries == -1:
        maxEntries = tree.GetEntries()

    # histogram name prefix
    histPrefix = 'h' + var + '_'

    # plot option
    plotOpt = 'e1'

    # histogram list
    histList = []

    # prepend HLT name
    testTrig = ['HLT_'+name.replace('HLT_','') for name in testTrig]

    # names
    if refTrig != '':
        refName = refTrig.replace('HLT_','')
    else:
        refName = 'Ref'

    rname = histPrefix + refName
    cname = 'canv_' + refName + var
    ctitle = 'Plots for reference:' + refTrig

    if cuts != '':
        ctitle += ' cut: ' + cuts

    if refTrig != '':
        cuts += ' && HLT_' + refTrig.replace('HLT_','')
        htitle = 'Ref: ' + refTrig
    else:
        htitle = 'Reference'

    # make canvas
    canv = TCanvas(cname,ctitle,800,800)

    # make hist
    nbins = 50

    varBinSize = False

    if var == 'MET':
        hRef = TH1F(rname,htitle,nbins,0,1000)
    elif var == 'HT':
        hRef = TH1F(rname,htitle,nbins,0,3000)
    elif 'pt' in var:
        xbins = range(5,50,5) + range(50,100,10) + range (100,225,25)#[10,20,30,40,60,80,100,150,200]
        hRef = TH1F(rname,htitle,len(xbins)-1,array('f',xbins))

        varBinSize = True
        #hRef = TH1F(rname,htitle,nbins,0,200)
    elif 'eta' in var:
        hRef = TH1F(rname,htitle,nbins,-2.5,2.5)
    else:
        hRef = TH1F(rname,htitle,nbins,0,1000)

    # make reference plot
    print 'Drawing', hRef.GetName(), 'with cuts', cuts

    tree.Draw(var + '>>' + hRef.GetName(),cuts,plotOpt, maxEntries)

    # axis set up
    hRef.SetStats(0)
    hRef.GetXaxis().SetTitle(var)
    #hRef.GetYaxis().SetRangeUser(0,2)
    canv.SetLogy()

    gPad.Update()

    _histStore[hRef.GetName()] = hRef
    histList.append(hRef)

    # loop over test triggers:
    for ind, trig in enumerate(testTrig):

        trigName = trig.replace('HLT_','')
        hname = 'h' + var + '_' + trigName

        hTest = hRef.Clone(hname)
        hTest.SetTitle(trigName)

        hTest.SetLineColor(_colorList[ind])

        # cuts

        if cuts != '':
            tcuts = cuts + ' && ' + trig
        else:
            tcuts = trig

        print 'Drawing', hTest.GetName(), 'with cuts', tcuts
        tree.Draw(var + '>>' + hTest.GetName(),tcuts,plotOpt+'same', maxEntries)

        gPad.Update()

        #hTest.Divide(hRef)

        _histStore[hTest.GetName()] = hTest
        histList.append(hTest)

    # if var bin sizes
    if varBinSize:
        for hist in histList:
            for bin in range(1,hist.GetNbinsX()+1):
                binC = hist.GetBinContent(bin)
                binW = hist.GetBinWidth(bin)

                binV = binC/binW
                #print binC, binW, binV

                hist.SetBinContent(bin, binV)

    #hRef.SetTitle(ctitle)

    # legend
    leg = canv.BuildLegend()
    leg.SetFillColor(0)
    #leg.SetHeader(ctitle.replace('&&','\n'));

    gPad.Update()

    _canvStore.append(canv)

    return histList

def plotEff(histList, var = 'HT', doFit = True):

    gStyle.SetOptTitle(0)

    ## histList: [hReference, hTest1, hTest2,...]

    # hist prefix
    histPrefix = 'h' + var + '_'

    # reference hist should be first
    hRef = histList[0]
    hRefEff = hRef.Clone(hRef.GetName()+'Eff')
    # set reference eff to 1
    hRefEff.Divide(hRef)

    hRefEff.GetYaxis().SetTitle("Efficiency")

    cname = 'canv_Eff_Ref' + hRefEff.GetName()
    ctitle = 'Eff for reference:' + hRefEff.GetName()

    ## make canvas
    canv = TCanvas(cname,ctitle,800,800)

    ## legend
    leg = getLegend('fit')

    # set reference eff to 1
    for bin in range(1,hRefEff.GetNbinsX()+1):
        hRefEff.SetBinContent(bin,1)
        hRefEff.SetBinError(bin,0)

    hRefEff.Draw()
    #leg.AddEntry(hRefEff,hRefEff.GetTitle(),'lp')

    plotOpt = 'same'

    gPad.Update()

    # loop over test
    #for ind,hname in enumerate(nameList):
    for ind,hist in enumerate(histList[1:]):

        #hist = _histStore[hname]
        hname = hist.GetName()

        # filter out hists
        #if histPrefix not in hname: continue
        #if 'Ref' in hname: continue

        htitle = hname.replace(histPrefix,'')
        hname = hname.replace('h','hEff')

        print 'Drawing', hname, 'from', hRef.GetName()

        ## Divide
        hEff = hist.Clone(hname)
        hEff.Divide(hRef)

        ## TEfficiency
        tEff = TEfficiency(hist,hRef)
        tEff.SetName(hname);#+';'+var+';Efficiency')
        tEff.SetTitle(htitle)

        # style
        tEff.SetLineColor(hist.GetLineColor())#_colorList[ind])
        tEff.SetFillColor(0)

        tEff.Draw(plotOpt)
        leg.AddEntry(tEff,tEff.GetTitle(),'l')

        if 'same' not in plotOpt: plotOpt += 'same'

        gPad.Update()

        #SetOwnership(tEff,0)

        if doFit:
            ## Fitting turn on curve
            print 'Fitting...'

            fturn = TF1("turnon",turnon_func,0,5000,3)
            fturn.SetParNames('halfpoint','width','plateau')
            fturn.SetParLimits(0,0,10000)
            fturn.SetParLimits(1,1,10000)
            fturn.SetParLimits(2,0,1)

            ## get painted graph and fit with turn-on
            gEff = tEff.GetPaintedGraph()
            #gEff = hEff

            ## get estimate of parameters
            expPlateau = hEff.GetMaximum()
            expHalfP = hEff.GetBinCenter(hEff.FindFirstBinAbove(0.1))
            expWidth = expHalfP/2

            #fturn.SetParameters(300,100,1)
            fturn.SetParameters(expHalfP,expWidth,expPlateau)

            ## do fit
            fitr = gEff.Fit(fturn,'S EX0')#EX0

            SetOwnership(gEff,0)

            halfpoint = fitr.Value(0)
            width = fitr.Value(1)
            plateau = fitr.Value(2)

            print 'Expected values: halfpoint = %5.2f, width = %5.2f, plateau = %5.2f' % (expHalfP, expWidth, expPlateau)
            print 'Fit result: halfpoint = %5.2f, width = %5.2f, plateau = %5.2f' % (halfpoint, width, plateau)

            gStyle.SetOptFit()
            #gStyle.SetOption("Show Fit Parameters")
            gPad.Update()

            _fitrStore.append((hname,halfpoint, width, plateau))

        _hEffStore[hname] = tEff

    # remove refEff
    #gPad.GetListOfPrimitives().Remove(hRef)

    # legend
    #leg = canv.BuildLegend()
    #leg.SetFillColor(0)
    leg.Draw()
    SetOwnership( leg, 0 )

    # axis set up
    hRefEff.SetStats(0)
    #hRef.GetXaxis().SetTitle(var)
    hRefEff.GetYaxis().SetRangeUser(0,1.5)
    #canv.SetLogy()

    #leg.GetListOfPrimitives().Remove(hRefEff)

    gPad.Update()

    _hEffStore[hRefEff.GetName] = hRefEff
    _canvStore.append(canv)

    return 1

if __name__ == "__main__":

    ## remove '-b' option
    _batchMode = False

    if '-b' in sys.argv:
        sys.argv.remove('-b')
        _batchMode = True

    if len(sys.argv) > 1:
        fileName = sys.argv[1]
        print '#fileName is', fileName
    else:
        print '#No file names given'
        exit(0)

    tfile  = TFile(fileName, "READ")

    if len(sys.argv) > 2:
        outName = sys.argv[2]
    else:
        print '#No out file name is given'
        outName = (os.path.basename(fileName)).replace('.root','_plots.root')
        print '#> Out file name is', outName

    outfile = TFile(outName, "RECREATE")

    if not tfile:
        print "Couldn't open the file"
        exit(0)

    # for friend trees
    tree = tfile.Get('sf/t')

    # for cmg trees
    #tree = tfile.Get('tree')

    nentries = tree.GetEntries()
    print 'Entries in tree:', nentries

    ## DEFINE plots
    # variable list
    varList = ['HT']#,'MET','ST']
    #varList = ['HT','LepGood1_pt']#,'LepGood1_eta']
    #varList = ['LepGood1_pt']

    # reference trigger (without HLT_)
    refTrig = ''

    # TEST triggers
    #testTrig = ['SingleMu','SingleEl','HT350','MET170']
    #testTrig = ['HT350','HT900','HTMET','MET170']#,'MuHT400MET70']
    #testTrig = ['HT350','HT600','HT900']
    testTrig = ['HT350']
    #testTrig = ['HT900', 'MuHad']
    #testTrig = ['HLT_SingleMu', 'HLT_MuNoIso', 'HLT_MuHad', 'HLT_MuHT600', 'HLT_MuHT400MET70','HLT_MuMET120', 'HLT_MuHT400B']
    #testTrig = ['HLT_SingleEl', 'HLT_ElNoIso', 'HLT_ElHad', 'HLT_EleHT600','HLT_EleHT400MET70','HLT_EleHT200', 'HLT_EleHT400B']
    #testTrig = ['HLT_SingleEl','HLT_ElNoIso','HLT_EleHT600']
    #testTrig = ['HLT_SingleMu','HLT_MuNoIso','HLT_MuHT600']
    #testTrig = ['HLT_SingleEl']

    # cuts
    cuts = ''
    #cuts = 'nTightEl == 1 && nVetoLeps == 0 && LepGood1_pt > 25'
    #cuts = 'nTightEl == 1 && LepGood1_pt > 15 && abs(LepGood1_eta) < 2.1'

    #print 'Split cuts:', cuts.split('&&')
    #print 'ReSplit cuts:', cutsToString(cuts.split('&&'))

    # max entries to process
    maxEntries = -1#100000

    doFit = True

    for var in varList:
        histList = getHistsFromTree(tree,var,refTrig, cuts, testTrig, maxEntries)
        plotEff(histList, var, doFit)

    ## save canvases to file
    prefix = 'fit_' + testTrig[0]+ refTrig + '_'

    for canv in _canvStore:
        pdir = 'plots/'
        canv.SaveAs(pdir+prefix+canv.GetName()+'.png')
        canv.Write()

    tfile.Close()
    ## wait
    if not _batchMode:
        answ = raw_input("Enter 'q' to exit: ")

    outfile.Close()
