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
            'HLT_HT350', 'HLT_HT600', 'HLT_HT900', 'HLT_MET170','HLT_HTMET', 'HLT_Had',
            'HLT_SingleMu', 'HLT_Mu45NoIso', 'HLT_Mu50NoIso', 'HLT_MuHad',
            'HLT_MuHT600', 'HLT_MuHT400MET70','HLT_MuHT350MET70','HLT_MuMET120', 'HLT_MuHT400B',
            'HLT_SingleEl', 'HLT_ElNoIso', 'HLT_ElHad',
            'HLT_EleHT600','HLT_EleHT400MET70','HLT_EleHT350MET70','HLT_EleHT200', 'HLT_ElHT400B',
            ## custom names
            'HLT_IsoMu27','HLT_IsoEle32'
            ]

    def listBranches(self):
        return self.branches[:]

    def __call__(self,event,base):

        # output dict:
        ret = {}

        '''
        ## check that any HLT branch exists in tree
        if not (hasattr(event,'HLT_SingleMu') or hasattr(event,'HLT_SingleEl')):
        #print 'Has no trigger info!'
        return ret
        '''

        ## loop over all HLT names and set them in tree
        for var in self.branches:
            #print var, getattr(event,var)
            if 'HLT_' in var and hasattr(event,var):
                ret[var] = getattr(event,var)

        # custom names fro triggers
        ret['IsoMu27'] = event.HLT_SingleMu
        ret['IsoEle32'] = event.HLT_SingleEl

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
