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
from readYields import getYield

def getYieldDict(cardFnames, region):
    yields = {}
    for cardFname in cardFnames:
        binname = os.path.basename(cardFname)
        binname = binname.replace('.merge.root','')
        tfile = TFile(cardFname,"READ")
        tfile.cd(region)
        dirList = gDirectory.GetListOfKeys()
        sourceYield = {}

        for k1 in dirList:
            h1 = k1.ReadObj().GetName()
            (yd, yerr)  = getYield(tfile, h1, region)
            sourceYield[h1] = (yd, yerr)
        yields[binname] = sourceYield

    return yields


def printBinnedTable(yields, name):
    f = open(name + '.tex','w')
    f.write('\\begin{table}[ht] \n ')
    binNames = sorted(yields.keys())
    singleSourceNames = sorted([ x.replace('x_','') for x in yields[binNames[0]].keys() if not('EWK' in x)])
    nSource = len(singleSourceNames)
    nCol = nSource + 3

    f.write('\\begin{tabular}{|' + (nCol *'%(align)s | ') % dict(align = 'c') + '} \n')
    f.write('\\hline')
    f.write('$L_T$ & $H_T$ & nB & ' +  ' %s ' % ' & '.join(map(str, singleSourceNames)) + ' \\\ \n')
    f.write(' $[$ GeV $]$  &   $[$GeV$]$ &  '  + (nSource *'%(tab)s  ') % dict(tab = '&') + ' \\\ \\hline \n')
    #write out all the counts
    for i,bin in enumerate(binNames):
        (LT, HT, B ) = bin.split("_")[0:3]        
        (LT0, HT0, B0 ) = ("","","") 
        if i > 0 :
            (LT0, HT0, B0 ) = binNames[i-1].split("_")[0:3]

        if LT != LT0:
            f.write(('\\cline{1-%s} ' + LT + ' & ' + HT + ' & ' + B) % (nCol))
        if LT == LT0 and HT != HT0:
            f.write(('\\cline{2-%s}  & ' + HT + ' & ' + B) % (nCol))
        elif LT == LT0 and HT == HT0:
            f.write('  &  & ' + B)
        for source in singleSourceNames:            
            f.write((' & %.2f $\pm$ %.2f') % yields[bin]['x_'+source])
        f.write(' \\\ \n')

    f.write('\\hline \n')
    f.write('\\end{tabular} \n')
    f.write('\\end{table} \n')   
    return


def printDataCardsFromMC(yields):
    signalPoint =  {'m1': ('mGlu','1500') , 'm2': ('mLSP','100') }
    signalName = ('%s_%s') % signalPoint['m1'] + ('_%s_%s') % signalPoint['m2']
    dataCardDir = 'datacards_' + signalName
    try:
        os.stat(inDir + '/' + dataCardDir)
    except:
        os.mkdir(inDir + '/' + dataCardDir)

    
    binNames = sorted(yields.keys())
    for binName in binNames:
        sig = {'x_' + signalName: (0.5 , 0.1)}
        myyields = yields[binName]
        myyields.update(sig)
        
        singleSourceNames = sorted([ x.replace('x_','') for x in myyields.keys() if not('EWK' in x or 'background' in x)])
        xsingleSourceNames = sorted([ x for x in myyields.keys() if not('EWK' in x or 'background' in x)])
        iproc = { key: i for (i,key) in enumerate(reversed(xsingleSourceNames))}
        print 'print ' + binName +'_.card.txt'
        datacard = open(inDir + '/' + dataCardDir + '/' + binName +'_.card.txt', 'w'); 
        datacard.write("## Datacard for cut file %s (signal %s)\n"%(binName,signalName))

        #datacard.write("shapes *        * ../common/%s.input.root x_$PROCESS x_$PROCESS_$SYSTEMATIC\n" % binName)
        datacard.write('##----------------------------------\n')
        datacard.write('bin         %s\n' % binName)
        datacard.write('observation %s\n' % myyields['x_background'][0])
        datacard.write('##----------------------------------\n')
        klen = len(singleSourceNames)
        kpatt = " %%%ds "  % klen
        fpatt = " %%%d.%df " % (klen,3)
        datacard.write('##----------------------------------\n')
        datacard.write('bin             '+(" ".join([kpatt % binName     for p in xsingleSourceNames]))+"\n")
        datacard.write('process         '+(" ".join([kpatt % p           for p in singleSourceNames]))+"\n")
        datacard.write('process         '+(" ".join([kpatt % iproc[p]    for p in xsingleSourceNames]))+"\n")
        datacard.write('rate            '+(" ".join([fpatt % myyields[p][0] for p in xsingleSourceNames]))+"\n")
        datacard.write('##----------------------------------\n')
        
        '''for name,effmap in systs.iteritems():
            datacard.write(('%-12s lnN' % name) + " ".join([kpatt % effmap[p]   for p in myprocs]) +"\n")
        for name,(effmap0,effmap12,mode) in systsEnv.iteritems():
            if mode == "templates":
                datacard.write(('%-10s shape' % name) + " ".join([kpatt % effmap0[p]  for p in myprocs]) +"\n")
            if mode == "envelop":
                datacard.write(('%-10s shape' % (name+"0")) + " ".join([kpatt % effmap0[p]  for p in myprocs]) +"\n")
            if mode in ["envelop", "shapeOnly"]:
                datacard.write(('%-10s shape' % (name+"1")) + " ".join([kpatt % effmap12[p] for p in myprocs]) +"\n")
                datacard.write(('%-10s shape' % (name+"2")) + " ".join([kpatt % effmap12[p] for p in myprocs]) +"\n")

        '''
        datacard.close()
        
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
    cardFnames = glob.glob(inDir+'/*/*.root')


    yields = getYieldDict(cardFnames, "SR_MB")
    printBinnedTable(yields, 'SR_table')
    printDataCardsFromMC(yields)
