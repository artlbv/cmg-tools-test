from CMGTools.TTHAnalysis.treeReAnalyzer import *
from ROOT import TLorentzVector, TVector2, std
import ROOT
import time
import itertools
import PhysicsTools.Heppy.loadlibs
import array
import operator

# pu histo file name
puFileName = "../python/tools/npv_ratio.root"
puHistName = "nVert_ratioDataOvMC"
puDict = {} # mc to data pu weight

puFile = ROOT.TFile(puFileName,"READ")
hPUw = puFile.Get(puHistName)

if not hPUw:
    print "PU hist not found!"
    exit(0)

for ibin in range(1,hPUw.GetNbinsX()):

    npv = hPUw.GetXaxis().GetBinLowEdge(ibin)
    rat = hPUw.GetBinContent(ibin)

    puDict[npv] = rat

puFile.Close()

print puDict

class EventVars1L_pileup:
    def __init__(self):
        self.branches = [
            'puRatio', 'nVtx'
            ]

    def listBranches(self):
        return self.branches[:]

    def __call__(self,event,base):

        # output dict:
        ret = {}

        if not event.isData:

            nVtx = event.nVert

            ret['nVtx'] = event.nVert

            if nVtx in puDict:
                puW = puDict[nVtx]
            else:
                puW = 0

            ret['puRatio'] = puW
        else:
            ret['puRatio'] = 1

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
