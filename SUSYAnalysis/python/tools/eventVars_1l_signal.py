from CMGTools.TTHAnalysis.treeReAnalyzer import *
from ROOT import TLorentzVector, TVector2, std
import ROOT
import time
import itertools
import PhysicsTools.Heppy.loadlibs
import array
import operator

# import gluino xsec table
#from glu_xsecs_v2 import xsecGlu

xsecGlu = {} # dict for xsecs
xsecFile = "../python/tools/glu_xsecs_13TeV.txt"

with open(xsecFile,"r") as xfile:
    lines = xfile.readlines()
    print 'Found %i lines in %s' %(len(lines),xsecFile)
    for line in lines:
        if line[0] == '#': continue
        (mGo,xsec,err) = line.split()
        #print 'Importet', mGo, xsec, err, 'from', line
        xsecGlu[int(mGo)] = (float(xsec),float(err))

    print 'Filled %i items to dict' % (len(xsecGlu))
    #print sorted(xsecGlu.keys())

cntsSusy = {} # dict for signal counts
#cntTotal = 0

#cntFile = "../python/tools/t1ttt_scan_counts.txt"
cntFile = "../python/tools/scans/counts_T1tttt_wSkim.txt"

with open(cntFile,"r") as cfile:
    lines = cfile.readlines()
    print 'Found %i lines in %s' %(len(lines),cntFile)

    for line in lines:
        if line[0] == '#': continue
        else:
            (mGo,mLSP,tot,totW,cnt,wgt) = line.split()
            #print 'Importet', mGo, mLSP, cnt, 'from', line
            #cntsSusy[(int(mGo),int(mLSP))] = (int(tot),int(cnt),float(wgt))
            cntsSusy[(int(mGo),int(mLSP))] = (float(totW),int(cnt),float(wgt))

    print 'Filled %i items to dict' % (len(cntsSusy))
    print "Finished signal parameter load"

# REMOVE LATER
import random

class EventVars1L_signal:
    def __init__(self):
        self.branches = [
            'mGo','mLSP','susyXsec',
            'susyNgen','totalNgen','susyWgen',
            ]

    def listBranches(self):
        return self.branches[:]

    def __call__(self,event,base):

        # output dict:
        ret = {}

        if not event.isData:

            ## MASS POINT
            mGo = 0
            mLSP = 0

            # Gluino Mass
            if hasattr(event,'GenSusyMGluino'): mGo = event.GenSusyMGluino

            # LSP Mass
            if hasattr(event,'GenSusyMNeutralino'): mLSP = event.GenSusyMNeutralino
            # set LSP mass of 1 to zero
            if mLSP == 1: mLSP = 0;

            # Fill for testing
            pseudoScan = False
            if pseudoScan:
                mGo = 0
                mLSP = 10

                while(mLSP > mGo):
                    mGo = random.randrange(500,1500,50)
                    mLSP = random.randrange(0,1500,50)

            # save masses
            ret['mGo'] = mGo; ret['mLSP'] = mLSP

            # SUSY Xsec
            if mGo in xsecGlu:
                ret['susyXsec'] = xsecGlu[mGo][0]
                #ret['susyXsecErr'] = xsecGlu[mGo][1]
            elif mGo > 0:
                print 'Xsec not found for mGo', mGo

            # Number of generated events
            #ret['totalNgen'] = cntTotal

            if (mGo,mLSP) in cntsSusy:
                ret['totalNgen'] = cntsSusy[(mGo,mLSP)][0]
                ret['susyNgen'] = cntsSusy[(mGo,mLSP)][1]
                ret['susyWgen'] = cntsSusy[(mGo,mLSP)][2]
            else:
                ret['totalNgen'] = 1
                ret['susyNgen'] = 1
                ret['susyWgen'] = 1

        return ret

if __name__ == '__main__':
    from sys import argv
    file = ROOT.TFile(argv[1])
    tree = file.Get("tree")
    class Tester(Module):
        def __init__(self, name):
            Module.__init__(self,name,None)
            self.sf = EventVars1L()
        def analyze(self,ev):
            print "\nrun %6d lumi %4d event %d: leps %d" % (ev.run, ev.lumi, ev.evt, ev.nLepGood)
            print self.sf(ev)
    el = EventLoop([ Tester("tester") ])
    el.loop([tree], maxEvents = 50)
