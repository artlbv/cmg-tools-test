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


# REMOVE LATER
import random

class EventVars1L_signal:
    def __init__(self):
        self.branches = [
            'mGo','mLSP','susyXsec'
            ]

    def listBranches(self):
        return self.branches[:]

    def __call__(self,event,base):

        # output dict:
        ret = {}

        if not event.isData:

            # Gluino Mass
            if hasattr(event,'GenSusyMGluino'):
                ret['mGo'] = event.GenSusyMGluino

            # LSP Mass
            if hasattr(event,'GenSusyMNeutralino'):
                ret['mLSP'] = event.GenSusyMNeutralino

            # Fill for testing
            if True:
                mGo = 0
                mLSP = 10

                while(mLSP > mGo):
                    mGo = random.randrange(500,1500,50)
                    mLSP = random.randrange(0,1500,50)

                ret['mGo'] = mGo; ret['mLSP'] = mLSP

            # SUSY Xsec
            if mGo in xsecGlu:
                ret['susyXsec'] = xsecGlu[mGo][0]
                #ret['susyXsecErr'] = xsecGlu[mGo][1]
            else:
                print 'Xsec not found for mGo', mGo

        # return branches
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
