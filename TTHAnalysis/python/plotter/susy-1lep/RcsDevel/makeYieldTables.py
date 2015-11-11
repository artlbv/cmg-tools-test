#!/usr/bin/env python
import sys

from yieldClass import *
from ROOT import *

def printLatexHeader(nCol, f):
    nCol = nCol + 4
    f.write('\\begin{table}[ht] \n ')
    f.write('\\tiny \n')
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

    pattern = "lumi3fb_puWeight/grid/merged/LT*NJ6*"
    yds6.addFromFiles(pattern,("lep","sele")) 
    pattern = "lumi3fb_puWeight/grid/merged/LT*NJ9*"
    yds9.addFromFiles(pattern,("lep","sele"))
    


    #pattern = 'arturstuff/grid/merged/LT\*NJ6\*'

    printSamps = ['TTsemiLep','TTdiLep','TTV','SingleT', 'WJets', 'DY', 'QCD','background']

    
    cats = ('SR_MB', 'CR_MB', 'SR_SB', 'CR_SB')
    for cat in cats:
        f =  open('yields' + cat + '.tex','w')
        samps = [('TTsemiLep',cat),('TTdiLep',cat),('TTV',cat), ('SingleT',cat), ('WJets',cat), ('DY',cat), ('QCD',cat), ('background',cat),]
        printLatexHeader(len(samps), f)
        label = 'Expected events in SR for 3 fbinv for njet 6,8 '
        yds6.printLatexTable(samps, printSamps, label,f) 
        label = 'Expected events in SR for 3 fb for njet $\\geq 9$'
        yds9.printLatexTable(samps, printSamps, label, f)
        printLatexFooter(f)
