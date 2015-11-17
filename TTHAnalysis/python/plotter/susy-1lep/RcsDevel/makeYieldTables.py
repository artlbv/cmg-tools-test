#!/usr/bin/env python
import sys

from yieldClass import *
from ROOT import *

def printLatexHeader(nCol, f):
    nCol = nCol + 4
    f.write('\\begin{table}[ht] \n ')
    f.write('\\footnotesize \n')
    f.write('\\caption{bla} \n')
    f.write('\\begin{tabular}{|' + (nCol *'%(align)s | ') % dict(align = 'c') + '} \n')
    f.write('\\hline \n')


def printLatexFooter(f):
    f.write('\\hline \n')
    f.write('\\end{tabular} \n')
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

    pattern = "Yields/MC/lumi3fb/full/*/merged/LT*NJ6*"
    yds6.addFromFiles(pattern,("lep","sele"))
    pattern = "Yields/MC/lumi3fb/full/*/merged/LT*NJ9*"
    yds9.addFromFiles(pattern,("lep","sele"))

    pattern = "Yields/data/lumi1p5fb_0p8scale/full/grid/merged/LT*NJ5*"
    yds5.addFromFiles(pattern,("lep","sele")) 
    


    #pattern = 'arturstuff/grid/merged/LT\*NJ6\*'

    printSamps = ['TTsemiLep','TTdiLep','TTV','SingleT', 'WJets', 'DY', 'QCD','background','T1t$^4$ 1.5$/$0.2','T1t$^4$ 1.5$/$0.9']

    
    cats = ('SR_MB', 'CR_MB', 'SR_SB', 'CR_SB')
    for cat in cats:
        f =  open('yields' + cat + '.tex','w')
        samps = [('TTsemiLep',cat),('TTdiLep',cat),('TTV',cat), ('SingleT',cat), ('WJets',cat), ('DY',cat), ('QCD',cat), ('background',cat),
('T1tttt_Scan_mGo1500_mLSP200',cat),('T1tttt_Scan_mGo1500_mLSP900',cat)]
        printLatexHeader(len(samps), f)
        yds6.showStats()
        label = 'Expected events in SR for 3 fbinv for njet 6,8 '
        yds6.printLatexTable(samps, printSamps, label,f) 
        label = 'Expected events in SR for 3 fb for njet $\\geq 9$'
        yds9.printLatexTable(samps, printSamps, label, f)
        printLatexFooter(f)



    f =  open('45j_test.tex','w')
    label = 'Counts and Rcs from 4jet sideband used to predict events in a 5jet signal region $5j_{SR} = Rcs^{4j,data} \\times \\kappa^{EWK, MC} \\times 5j_{CR}$'
    printSamps = ['data 4j, SR','(data-QCD) 4j, CR','data 4j, Rcs$^{EWK}$','$\\kappa^{EWK}$, MC','(data-QCD) 5j, CR', 'data 5j, pred', 'data 5j, SR', 'MCx0.8 5j,SR']

    #    samps = [('data','SR_SB'),('data','CR_SB'),('data','Rcs_SB'),('EWK','Kappa'),('data','CR_MB'),('data','SR_MB_predict'), ('data','SR_MB'), ('background','SR_MB')]
    samps = [('data_QCDsubtr','SR_SB'),('data_QCDsubtr','CR_SB'),('data_QCDsubtr','Rcs_SB'),('EWK','Kappa'),('data_QCDsubtr','CR_MB'),('data_QCDsubtr','SR_MB_predict'), ('data_QCDsubtr','SR_MB'), ('EWK','SR_MB')]
    printLatexHeader(len(samps), f)
    yds5.printLatexTable(samps, printSamps, label,f) 
    printLatexFooter(f)
