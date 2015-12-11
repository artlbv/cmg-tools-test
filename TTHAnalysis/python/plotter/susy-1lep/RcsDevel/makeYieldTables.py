#!/usr/bin/env python
import sys

from yieldClass import *
from ROOT import *

def printLatexHeader(nCol, f, sideways = 0):
    nCol = nCol + 4
    print f.name
    name = f.name.replace('yields','').replace('.tex','').replace('_','')
    name = name.replace('SR','signal region')
    name = name.replace('CR','control region')
    name = name.replace('MB',', main band')
    name = name.replace('SB',', side band')
    print name
    if sideways == 1:
        f.write('\\begin{sidewaystable}[ht] \n ')
        f.write('\\tiny \n')
        f.write('\\caption{ Expected event yields in ' + name + ' for the multi-b analysis in the search bins as defined in Table~\\ref{tab:1b_sigreg_3fb}. The \\DF is adjusted for each \\LT bin. The contribution of dileptonic \\ttbar events is shown separately, where leptons can be either electrons, muons, or taus.} \n')

    elif sideways == 2:
        f.write('\\begin{sidewaystable}[ht] \n ')
        f.write('\\tiny \n')
        f.write('\\caption{ Test of the background prediction method using the exclusive 4 jet category as a side band to predict the expected number of events in the signal regin of an exclusive 5 jet main band.} \n')
    elif sideways == 3:
        f.write('\\begin{sidewaystable}[ht] \n ')
        f.write('\\tiny \n')
        f.write('\\caption{Background prediction based on the [4,5] jet side band in the [6,8] and $\geq$ 9 jet signal regions. The oberseved events in the SR, MB are still blinded.} \n')

    else:

        f.write('\\begin{table}[ht] \n ')
        f.write('\\footnotesize \n')
        f.write('\\caption{'+name+'} \n')

    
    f.write('\\label{tab:'+f.name.replace('.tex','')+'} \n')
    f.write('\\begin{tabular}{|' + (nCol *'%(align)s | ') % dict(align = 'c') + '} \n')
    f.write('\\hline \n')


def printLatexFooter(f, sideways = 0):
    f.write('\\hline \n')
    f.write('\\end{tabular} \n')
    if sideways > 0:
        f.write('\\end{sidewaystable} \n ')
    else:
        f.write('\\end{table} \n')   

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

    ## Create Yield Storage

    yds6 = YieldStore("lepYields")
    yds9 = YieldStore("lepYields")
    yds5 = YieldStore("lepYields")

    pattern = "Yields/all/lumi2p1fb_MC1_2fbbins_noPU/full/*/merged/LT*NJ6*"
    yds6.addFromFiles(pattern,("lep","sele"))
    pattern = "Yields/all/lumi2p1fb_MC1_2fbbins_noPU/full/*/merged/LT*NJ9*"
    yds9.addFromFiles(pattern,("lep","sele"))

    pattern = "Yields/all/lumi2p1fb_MC1_2fbbins_noPU/full/grid/merged/LT*NJ5*"
    yds5.addFromFiles(pattern,("lep","sele")) 
    


    #pattern = 'arturstuff/grid/merged/LT\*NJ6\*'

    printSamps = ['TTsemiLep','TTdiLep','TTV','SingleT', 'WJets', 'DY', 'QCD','background','T1t$^4$ 1.5$/$0.1','T1t$^4$ 1.2$/$0.8']

    if 1 ==1:
        cats = ('SR_MB', 'CR_MB', 'SR_SB', 'CR_SB')
        for cat in cats:
            f =  open('yields' + cat + '.tex','w')
            samps = [('TTsemiLep',cat),('TTdiLep',cat),('TTV',cat), ('SingleT',cat), ('WJets',cat), ('DY',cat), ('QCD',cat), ('background',cat),
                     ('T1tttt_Scan_mGo1500_mLSP100',cat),('T1tttt_Scan_mGo1200_mLSP800',cat)]
            printLatexHeader(len(samps), f, 1)
            yds6.showStats()
            srcr = cat.replace('_MB','').replace('_SB','')
            sbmb = cat.replace('SR_','').replace('CR_','')
            label = 'Expected events in '+srcr+' for 2.1 fb$^{-1}$ for '+sbmb.replace('MB','$n_{jet}$ 6,8 ').replace('SB','$n_{jet}$ 4,5 for 6,8')
            yds6.printLatexTable(samps, printSamps, label,f) 
            label = 'Expected events in SR for 2.1 fb$^{-1}$ for '+sbmb.replace('MB','$n_{jet}$ $\\geq 9$').replace('SB','$n_{jet}$ 4,5 for $\\geq 9$')
            yds9.printLatexTable(samps, printSamps, label, f)
            printLatexFooter(f, 2)
            f.close()


    f =  open('4to5j_preditiction.tex','w')
    label = 'Counts and Rcs from 4jet sideband used to predict events in a 5jet signal region $5j_{SR} = Rcs^{4j,data} \\times \\kappa^{EWK, MC} \\times 5j_{CR}$'
    printSamps = ['data 4j, SR','(data-QCD) 4j, CR','data 4j, Rcs$^{EWK}$','$\\kappa^{EWK}$, MC','(data-QCD) 5j, CR', 'data 5j, pred', 'data 5j, SR', 'MC 5j,SR']
    samps = [('data_QCDsubtr','SR_SB'),('data_QCDsubtr','CR_SB'),('data_QCDsubtr','Rcs_SB'),('EWK','Kappa'),('data_QCDsubtr','CR_MB'),('data_QCDsubtr','SR_MB_predict'), ('data_QCDsubtr','SR_MB'), ('EWK','SR_MB')]

    #in case one wants more details
    #printSamps = ['data 4j, SR','data 4j, CR','QCD 4j,CR','(data-QCD) 4j, CR','data 4j, Rcs$^{EWK}$','$\\kappa^{EWK}$, MC','data 5j, CR','QCD 5j, CR','(data-QCD) 5j, CR'] 
    #samps = [('data_QCDsubtr','SR_SB'),('data','CR_SB'),('data_QCDpred','CR_SB'),('data_QCDsubtr','CR_SB'),('data_QCDsubtr','Rcs_SB'),('EWK','Kappa'),('data','CR_MB'),('data_QCDpred','CR_MB'),('data_QCDsubtr','CR_MB')]
    printLatexHeader(len(samps), f, 2)
    yds5.printLatexTable(samps, printSamps, label,f) 
    printLatexFooter(f, 2)
    f.close()

    label = 'Counts and Rcs from 45jet sideband used to predict events in a >= 6 jet signal region $5j_{SR} = Rcs^{4j,data} \\times \\kappa^{EWK, MC} \\times 5j_{CR}$'
    f =  open('4to68_4to9j_prediction.tex','w')

    printLatexHeader(len(samps), f, 3)
    yds6.showStats()
    label = 'SB, MB, and predictions for 2.1 fb$^{-1}$ for $n_{jet}$ 6,8 '
    printSamps = ['data 45j, SR','(data-QCD) 4j5, CR','data 4j5, Rcs$^{EWK}$','$\\kappa^{EWK}$, MC','(data-QCD) 68j, CR', 'data 68j, pred', 'data 68j, SR', 'MC 68j,SR']
    yds6.printLatexTable(samps, printSamps, label,f) 
    label = 'SB, MB, and predictions for 2.1 fb$^{-1}$ for njet $\\geq 9$'
    printSamps = ['data 45j, SR','(data-QCD) 4j5, CR','data 4j5, Rcs$^{EWK}$','$\\kappa^{EWK}$, MC','(data-QCD) 9ij, CR', 'data 9ij, pred', 'data 9ij, SR', 'MC 9ij,SR']
    yds9.printLatexTable(samps, printSamps, label, f)
    printLatexFooter(f, 3)
    f.close()


    f =  open('RCS_mc.tex','w')
    label = 'Rcs values from SB and MB and kappa'

    printSamps = ['$R_{CS}$ [6,8] jets','$R_{CS}$ [4,5] jets','$\kappa$']
    samps = [('EWK','Rcs_MB'),('EWK','Rcs_SB'),('EWK','Kappa')]
    printLatexHeader(len(samps), f)
    yds6.printLatexTable(samps, printSamps, label,f) 
    printSamps = ['$R_{CS}$ $\geq$ 9 jets','$R_{CS}$ [4,5] jets','$\kappa$']
    samps = [('EWK','Rcs_MB'),('EWK','Rcs_SB'),('EWK','Kappa')]
    yds9.printLatexTable(samps, printSamps, label,f) 
    printLatexFooter(f)
    f.close()
