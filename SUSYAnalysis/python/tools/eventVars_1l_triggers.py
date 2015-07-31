from CMGTools.TTHAnalysis.treeReAnalyzer import *
from ROOT import TLorentzVector, TVector2, std
import ROOT
import time
import itertools
import PhysicsTools.Heppy.loadlibs
import array
import operator

class EventVars1L_triggers:
    def __init__(self):
        self.branches = [
            'HLT_HT350', 'HLT_HT600', 'HLT_HT800','HLT_HT900',
            'HLT_MET170',
            'HLT_HT350MET120','HLT_HT350MET100',
            'HLT_SingleMu', 'HLT_Mu50NoIso'
            'HLT_MuHT600', 'HLT_MuHT400MET70','HLT_MuHT350MET70','HLT_MuMET120', 'HLT_MuHT400B',
            'HLT_SingleEl', 'HLT_ElNoIso',
            'HLT_EleHT600','HLT_EleHT400MET70','HLT_EleHT350MET70','HLT_EleHT200', 'HLT_ElHT400B',
            ## custom names
            'HLT_IsoMu27','HLT_IsoEle32',
            'HLT_Mu50','HLT_Ele105'
            ]

    def listBranches(self):
        return self.branches[:]

    def __call__(self,event,base):

        # output dict:
        ret = {}

        #for line in vars(event)['_tree'].GetListOfBranches():
        #    if 'HLT_' in line.GetName():
        #        print line.GetName()


        # custom names for triggers
        ret['HLT_IsoMu27'] = event.HLT_SingleMu
        ret['HLT_IsoEle32'] = event.HLT_SingleEl
        ret['HLT_Mu50'] = event.HLT_Mu50NoIso
        ret['HLT_Ele105'] = event.HLT_ElNoIso

        ## loop over all HLT names and set them in tree
        for var in self.branches:
            #print var, getattr(event,var)
            if 'HLT_' in var and hasattr(event,var):
                ret[var] = getattr(event,var)

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
