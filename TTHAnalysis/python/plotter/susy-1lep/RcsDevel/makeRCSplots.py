#!/usr/bin/env python
#Script to read data cards and turn them either into a table that can be copied to Excel/OpenOffice
#1;2cor print out in latex format.

import shutil
import subprocess
import os
import sys
import glob
from multiprocessing import Pool
from ROOT import *
import math
from printTableDataCards import *
from searchBins import *
from array import array

gROOT.SetBatch(kTRUE) 
gStyle.SetOptStat(kFALSE)
f = TFile('RCS_kappa_plost.root',"recreate")
f2 = TFile('bkgFrac_plots.root',"recreate")
######################GLOBAL VARIABLES PUT IN OPTIONS############
ignoreEmptySignal = True
def makeRCSPlot(yieldsList, dimension, source = 'EWK'):
    binNames = sorted(yieldsList[0][0].keys())
    graphs = []
    
    hists = []
    (dim, outname) = dimension.split('_')[0:2]
    for yields in yieldsList:
        h = TH1F("test", "test", 25, 0, 25)
        x = []
        y = []
        name = []
        i = 0
        for bin in binNames:
            (LTbin, HTbin, Bbin ) = bin.split("_")[0:3]
            (LT, HT, B) = (binsLT[LTbin][1].replace('$',''), binsHT[HTbin][1].replace('$',''), binsNB[Bbin][1].replace('$',''))
            if dim in HTbin or dim in LTbin or dim in Bbin:
                i = i+1
                print LTbin, Bbin, HTbin, yields[0][bin][source][0]
                
                h.SetBinContent(i,yields[0][bin][source][0])
                h.SetBinError(i,yields[0][bin][source][1])

                if 'NB' in dim:h.GetXaxis().SetBinLabel(i, '' + LTbin + ', ' + HTbin)
                if 'LT' in dim:h.GetXaxis().SetBinLabel(i, '' + Bbin + ', ' + HTbin)
                if 'HT' in dim:h.GetXaxis().SetBinLabel(i, '' + Bbin + ', ' + LTbin)
        h.GetXaxis().SetRangeUser(0,i)
        h.GetXaxis().SetLabelSize(0.07)
        
        mid = ''
        if 'NB' in dim: mid = ', nB ='+ binsNB[dim][1].replace('$\geq$','>=').replace('$=$','=')
        if 'LT' in dim: mid = ', LT ' + binsLT[dim][1].replace('$\geq$','>=').replace('$','')
        if 'HT' in dim: mid = ', HT ' + binsHT[dim][0].replace('$\geq$','>=').replace('$','')
        h.SetTitle(yields[1] + mid + ', '+ source)
        hists.append(h)

    c = TCanvas("canvas", "canvas", 800 , 700)
    c.Divide(0,2)
    for i,h in enumerate(hists):
        h.SetLineColor(i+1)
        h.SetMarkerStyle(20+i)
        h.SetMarkerColor(i+1)
        h.SetLineWidth(2)
        line = TF1("line","1", 0, 20)
        line.SetLineColor(kRed)
        if i < 2:
            c.cd(1)
            h.GetYaxis().SetRangeUser(0,0.2)
            if 'TTdi' in source:
                h.GetYaxis().SetRangeUser(0,0.8)
            if 'TTV' in source:
                h.GetYaxis().SetRangeUser(0,0.5)
                
            h.Draw('same')


        else:
            h.SetLineColor(1)
            h.SetMarkerColor(1)
            c.cd(2)
            h.Draw()
            h.GetYaxis().SetRangeUser(0,2)
            c.GetPad(2).BuildLegend()
            line.Draw("same")
    c.GetPad(1).BuildLegend()

    c.SetName(dim + "_"+outname+'_'+source)
    f.cd()
    c.Write()
    c.SaveAs('RCSplots/'+dim + "_"+outname+'_'+source+'.pdf')


    return 

def makeSBMBtable(yieldsList, dimension, source = 'EWK'):

    binNames = sorted(yieldsList[0][0].keys())
    graphs = []

    hists = []
    (dim, outname) = dimension.split('_')[0:2]
    for bin in binNames:
        (LTbin, HTbin, Bbin ) = bin.split("_")[0:3]
        if dim in HTbin or dim in LTbin or dim in Bbin:
#            singleSourceNames = ['TTdiLep','TTsemiLep','Wjets']
            singleSourceNames = ['EWK','TT','TTdiLep','TTsemiLep','WJets','TTV','SingleT','DY']
            print bin
            for yields in yieldsList:
                total = yields[0][bin]['EWK'][0]
                for source in singleSourceNames:
                    print source, yields[0][bin][source][0], yields[0][bin][source][0]/total
            print 
   
    return 

colorDict = {'TT': kBlue-4,'TTdiLep':kBlue,'TTsemiLep':kBlue+1,'WJets':kGreen-2,
'QCD':kCyan-6,'SingleT':kViolet+5,'DY':kRed-6,'TTV':kOrange-3}
def makeFracPlots(yieldsList, dimension, source = 'EWK'):

    binNames = sorted(yieldsList[0][0].keys())
    graphs = []
    
    hists = []
    xbins = 20
    (dim, outname) = dimension.split('_')[0:2]
    singleSourceNames = ['TTdiLep','TTsemiLep','WJets','TTV','SingleT','DY']
    
    for yields in yieldsList:

        hstack = THStack("hs","")
        for j,source in enumerate(singleSourceNames):
            h = TH1F("test", "test", 25, 0, 25) 
            i=0
            for bin in binNames:
                (LTbin, HTbin, Bbin ) = bin.split("_")[0:3]
                if dim in HTbin or dim in LTbin or dim in Bbin:
                    i = i + 1
                    total = yields[0][bin]['EWK'][0]
                    
                    print source, yields[0][bin][source][0], yields[0][bin][source][0]/total
                    h.SetBinContent(i, yields[0][bin][source][0]/total)

                    if 'NB' in dim:h.GetXaxis().SetBinLabel(i, '' + LTbin + ', ' + HTbin)
                    if 'LT' in dim:h.GetXaxis().SetBinLabel(i, '' + Bbin + ', ' + HTbin)
                    if 'HT' in dim:h.GetXaxis().SetBinLabel(i, '' + Bbin + ', ' + LTbin)
            print 'bins', i
            xbins = i
            h.GetXaxis().SetLabelSize(0.07)
            h.SetFillColor(colorDict[source])
            mid = ''
            if 'NB' in dim: mid = ', nB ='+ binsNB[dim][1].replace('$\geq$','>=').replace('$=$','=')
            if 'LT' in dim: mid = ', LT ' + binsLT[dim][1].replace('$\geq$','>=').replace('$','')
            if 'HT' in dim: mid = ', HT ' + binsHT[dim][0].replace('$\geq$','>=').replace('$','')
            hstack.SetTitle(yields[1] + mid + ', '+ ' bkg fractions')
            hstack.Add(h)
        
        hists.append(hstack)

    c = TCanvas("canvas", "canvas", 900 , 700)
    print len(hists)
    for i,h in enumerate(hists):
        
        h.Draw('')
        h.GetXaxis().SetRangeUser(0,xbins)
        c.SetName(dim + "_"+outname+'_'+yieldsList[i][1].replace(' ','').replace(',',''))
        c.SaveAs('FracPlots/'+dim + "_"+outname+'_'+yieldsList[i][1].replace(' ','').replace(',','')+'.pdf')

        f2.cd()
        c.Write()

    return 



# MAIN
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cardDirectory = sys.argv[1]
    else:
        print "Will stop, give input Dir"
        quit()

    cardDirectory = os.path.abspath(cardDirectory)
    cardDirName = os.path.basename(cardDirectory)

    print 'Using cards from', cardDirName
    inDir = cardDirectory
    cardFnames = glob.glob(inDir+'/*/*68*.root')
    cardFnames9 = glob.glob(inDir+'/*/*9i*.root')
    
    for i,cards in enumerate((cardFnames, cardFnames9)):
        dictRcs_MB = getYieldDict(cards,"Rcs_MB","","lep")
        dictRcs_SB = getYieldDict(cards,"Rcs_SB","","lep")
        dictKappa = getYieldDict(cards,"Kappa","","lep")

        dictSR_MB = getYieldDict(cards,"SR_MB","","lep")
        dictSR_SB = getYieldDict(cards,"SR_SB","","lep")
        dictCR_MB = getYieldDict(cards,"CR_MB","","lep")
        dictCR_SB = getYieldDict(cards,"CR_SB","","lep")

        
        if i==0: jets = '6-8'
        if i==1: jets = '9-i'
        sourceList = ['EWK','TT','TTincl','TTdiLep','TTsemiLep','WJets','TTV']
        for source in sourceList:
            makeRCSPlot(((dictRcs_MB, jets.replace('-',', ')+' jets'), (dictRcs_SB , ' 4,5 jets'), (dictKappa, '#kappa')),'NB0_'+jets+'RCS', source)
            makeRCSPlot(((dictRcs_MB, jets.replace('-',', ')+' jets'), (dictRcs_SB , ' 4,5 jets'), (dictKappa, '#kappa')),'NB1_'+jets+'RCS', source)
            makeRCSPlot(((dictRcs_MB, jets.replace('-',', ')+' jets'), (dictRcs_SB , ' 4,5 jets'), (dictKappa, '#kappa')),'NB2_'+jets+'RCS', source)
            makeRCSPlot(((dictRcs_MB, jets.replace('-',', ')+'jets'), (dictRcs_SB , ' 4,5 jets'), (dictKappa, '#kappa')),'NB3i_'+jets+'RCS', source)
            makeRCSPlot(((dictRcs_MB, jets.replace('-',', ')+'jets'), (dictRcs_SB , ' 4,5 jets'), (dictKappa, '#kappa')),'LT1_'+jets+'RCS', source)
            makeRCSPlot(((dictRcs_MB, jets.replace('-',', ')+'jets'), (dictRcs_SB , ' 4,5 jets'), (dictKappa, '#kappa')),'LT2_'+jets+'RCS', source)
            makeRCSPlot(((dictRcs_MB, jets.replace('-',', ')+'jets'), (dictRcs_SB , ' 4,5 jets'), (dictKappa, '#kappa')),'LT3_'+jets+'RCS', source)
            makeRCSPlot(((dictRcs_MB, jets.replace('-',', ')+'jets'), (dictRcs_SB , ' 4,5 jets'), (dictKappa, '#kappa')),'LT4i_'+jets+'RCS', source)

        if 1==2:
            makeFracPlot(((dictSR_MB, jets.replace('-',', ')+'jets'), (dictSR_SB , ' 4,5 jets'),),'NB0_'+jets+'Frac')
        if 1==1:
            #makeSBMBtable(((dictCR_MB, 'CR '+ jets.replace('-',', ')+'jets'), (dictCR_SB , ' CR 4,5 jets'), (dictSR_MB, 'SR '+ jets.replace('-',', ')+'jets'), (dictSR_SB , ' SR 4,5 jets'), ),'NB1_'+jets+'Frac')
            print  ' '
            makeFracPlots(((dictCR_MB, 'CR '+ jets.replace('-',', ')+'jets'), (dictCR_SB , ' CR 4,5 jets'), (dictSR_MB, 'SR '+ jets.replace('-',', ')+'jets'), (dictSR_SB , ' SR 4,5 jets'), ),'NB1_'+jets+'Frac')
            makeFracPlots(((dictCR_MB, 'CR '+ jets.replace('-',', ')+'jets'), (dictCR_SB , ' CR 4,5 jets'), (dictSR_MB, 'SR '+ jets.replace('-',', ')+'jets'), (dictSR_SB , ' SR 4,5 jets'), ),'NB2_'+jets+'Frac')
            makeFracPlots(((dictCR_MB, 'CR '+ jets.replace('-',', ')+'jets'), (dictCR_SB , ' CR 4,5 jets'), (dictSR_MB, 'SR '+ jets.replace('-',', ')+'jets'), (dictSR_SB , ' SR 4,5 jets'), ),'NB3i_'+jets+'Frac')
            #makeSBMBtable(((dictCR_MB, 'CR '+ jets.replace('-',', ')+'jets'), (dictCR_SB , ' CR 4,5 jets'), (dictSR_MB, 'SR '+ jets.replace('-',', ')+'jets'), (dictSR_SB , ' SR 4,5 jets'), ),'NB2_'+jets+'Frac')
        if 1==2 and i==0:
            makeSBMBtable(((dictCR_MB, 'CR '+ jets.replace('-',', ')+'jets'), (dictCR_SB , ' CR 4,5 jets'), (dictSR_MB, 'SR '+ jets.replace('-',', ')+'jets'), (dictSR_SB , ' SR 4,5 jets'), ),'NB1_'+jets+'Frac')
            makeSBMBtable(((dictCR_MB, 'CR '+ jets.replace('-',', ')+'jets'), (dictCR_SB , ' CR 4,5 jets'), (dictSR_MB, 'SR '+ jets.replace('-',', ')+'jets'), (dictSR_SB , ' SR 4,5 jets'), ),'NB2_'+jets+'Frac')
            makeSBMBtable(((dictCR_MB, 'CR '+ jets.replace('-',', ')+'jets'), (dictCR_SB , ' CR 4,5 jets'), (dictSR_MB, 'SR '+ jets.replace('-',', ')+'jets'), (dictSR_SB , ' SR 4,5 jets'), ),'NB3i_'+jets+'Frac')




        
