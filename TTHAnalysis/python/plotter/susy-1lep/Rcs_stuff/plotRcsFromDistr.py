#!/usr/bin/python

import sys
import os
#sys.argv.append( '-b' )

from ROOT import *
from array import array

_histListSR = []
_histListCR = []
_histListRcs = []

_canvStore = []
_histStore = []

def getHistsFromFile(tfile, sample = 'background'):

    print '# Getting hist from sample', sample

    for key in tfile.GetListOfKeys():
        hist = key.ReadObj()

        if 'TH1' in str(type(hist)):
            ## skip inclusive ST
            if 'ST_'+sample == hist.GetName(): continue
            #if 'background' in hist.GetName():
            if sample in hist.GetName():
                hname = hist.GetName()

                ## determine SR or CR
                if 'SR' in hname:
                    _histListSR.append(hist.Clone(hname))
                elif 'CR' in hname:
                    _histListCR.append(hist.Clone(hname))
    return 1

def getRcsPlots():

    for indx,histSR in enumerate(_histListSR):

        hname = (histSR.GetName()).replace('SR','Rcs')

        histRcs = histSR.Clone(hname)
        histRcs.Divide(_histListCR[indx])

        _histListRcs.append(histRcs)

    return 1

def setColors(histList):

    colorList = [1,2,4,7,3,6,8,9] + range(10,50)

    histNj45 = [hist for hist in histList if 'NJ45' in hist.GetName()]

    for ind,hist in enumerate(histNj45):

        hist.SetLineColor(colorList[ind])
        hist.SetMarkerColor(colorList[ind])

    histRest = [hist for hist in histList if 'NJ45' not in hist.GetName()]

    for ind,hist in enumerate(histRest):

        hist.SetLineColor(colorList[ind])
        hist.SetMarkerColor(colorList[ind])
        hist.SetLineStyle(2)

def custHists():
    ## loop over all saved hists
    for hist in _histListCR+_histListSR:

        hname = hist.GetName()
        ## common settings
        hist.SetStats(0)
        hist.SetFillColor(0)
        hist.SetLineWidth(2)
        hist.SetMarkerStyle(0)

        ## rebin
        #hist.Rebin(2)

        htitle = ''
        ## NJ bins
        if 'NJ45'in hname:
            htitle = 'Nj #in [4,5] '
        elif 'NJ6i'in hname:
            htitle = 'Nj #geq 6 '
        elif 'NJ68'in hname:
            htitle = 'Nj #in [6,8] '
        elif 'NJ9i'in hname:
            htitle = 'Nj #geq 9 '

        #if 'NJ' in hname and 'HT' in hname: htitle += '; '

        ## HT bins
        if 'HT500750'in hname:
            htitle += '500 < HT < 750'
        elif 'HT7501000'in hname:
            htitle += '750 < HT < 1000'
        elif 'HT5001000'in hname:
            htitle += '500 < HT < 1000'
        elif 'HT7501250'in hname:
            htitle += '750 < HT < 1250'
        elif 'HT1250'in hname:
            htitle += 'HT > 1250'
        elif 'HT1000'in hname:
            htitle += 'HT > 1000'
        elif 'HT500'in hname:
            htitle += 'HT > 500'
        elif 'HT750'in hname:
            htitle += 'HT > 750'

        hist.SetTitle(htitle)

        print hname, htitle

        setColors(_histListSR)
        setColors(_histListCR)

    return 1

def plotHists(flag = 'CR', doNorm = False, plotOpt = 'histe1'):

    if flag == 'CR':
        histList = _histListCR
    elif flag == 'SR':
        histList = _histListSR
    elif flag == 'Rcs':
        histList = _histListRcs
        plotOpt += 'e1'

    hname = histList[0].GetName()
    varName = hname[:hname.find('_')]

    # define Canvas (plot) name
    cname = 'canv_'+ varName + '_' + flag

    if doNorm == True:
        cname += 'Norm'

    canv = TCanvas(cname,varName+' in different bins for '+ flag,800,800)

    ## clone hists for this plot
    histCloneList = []

    #for hist in histList:
    #histCloneList.append(hist.Clone(hist.GetName()+cname))

    #histList = histCloneList

    for ind,hist in enumerate(histList):

        #_histStore.append(hist)
        #print 'Hist name', hist.GetName()

        if doNorm:
            hist.DrawNormalized(plotOpt)
        else:
            hist.Draw(plotOpt)

        if 'same' not in plotOpt: plotOpt += 'same'

    leg = canv.BuildLegend()
    leg.SetFillColor(0)

    # set proper title
    first =  canv.GetListOfPrimitives()[0]
    first.SetTitle(canv.GetTitle())

    # Set ST/LT range
    if 'ST' in varName or 'LT' in varName:
        first.GetXaxis().SetRangeUser(250,1000)
    elif 'HT' in varName:
        first.GetXaxis().SetRangeUser(500,2000)

    # axis label
    first.GetXaxis().SetLabelSize(0.04)
    first.GetYaxis().SetLabelSize(0.04)

    # axis titles
    first.GetXaxis().SetTitleSize(0.05)

    first.GetYaxis().SetTitleSize(0.04)
    first.GetYaxis().SetTitleOffset(1.0)


    # Y axis mod
    if flag != 'Rcs':
        canv.SetLogy()

        if doNorm:
            first.GetYaxis().SetTitle("a.u.")
            first.GetYaxis().SetRangeUser(0.001,0.8)
    else:
        first.GetYaxis().SetTitle("R_{CS}")

        # fix Y axis for different samples:
        if 'TT_DiLep' in hname:
            first.GetYaxis().SetRangeUser(0,2.9)
        elif 'TT_Rest' in hname:
            first.GetYaxis().SetRangeUser(0,0.29)
        elif 'WJets' in hname:
            first.GetYaxis().SetRangeUser(0,0.29)
        elif 'TTV' in hname:
            first.GetYaxis().SetRangeUser(0,0.79)
        else:
            first.GetYaxis().SetRangeUser(0,0.79)

    _canvStore.append(canv)
    return canv

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
    indir = os.path.dirname(fileName)

    if len(sys.argv) > 2:
        outName = sys.argv[2]
    else:
        print '#No out file name is given'
        outName = (os.path.basename(fileName)).replace('.root','_rcs.root')
        print '#> Out file name is', outName

    outfile = TFile(outName, "RECREATE")

    if not tfile:
        print "Couldn't open the file"
        exit(0)

    samples = ['TT_DiLep','TT_Rest','TTV','WJets','SingleT']#,'DY']
    samples += ['background']
    #samples = ['TT_DiLep','TTV']
    #samples = ['TT_Rest','WJets']

    for samp in samples:

        _histListSR = []
        _histListCR = []
        _histListRcs = []

        _canvStore = []
        _histStore = []

        # get hists from files
        getHistsFromFile(tfile,samp)

        #print _histListCR
        #print _histListSR

        # customise hists
        custHists()

        # make rcs plots
        getRcsPlots()

        #canvCRnorm = plotHists('CR',True)
        #canvSRnorm = plotHists('SR',True)
        canvRcs = plotHists('Rcs')

        if not _batchMode:
            ## wait
            answ = raw_input("Enter 'q' to exit: ")
            if 'q' in answ: exit(0)

        #canvCR = plotHists('CR')
        #canvSR = plotHists('SR')

        ## save canvases
        pdir = indir

        if not os.path.exists(pdir):
            os.makedirs(pdir)

        extList = ['.pdf','.png']
        for canv in _canvStore:

            for ext in extList:
                cname = '/'+samp+'_'+ canv.GetName()+ext
                canv.SaveAs(pdir+cname)

            canv.Write()

    tfile.Close()
    outfile.Close()
