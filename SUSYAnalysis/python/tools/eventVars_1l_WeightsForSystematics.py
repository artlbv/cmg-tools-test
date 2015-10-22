from CMGTools.TTHAnalysis.treeReAnalyzer import *
import ROOT


class EventVars1LWeightsForSystematics:
    def __init__(self):
        self.branches = ["GenTopPt", "GenAntiTopPt", "TopPtWeight"
                         ]

    def listBranches(self):
        return self.branches[:]

    def __call__(self,event,keyvals):
        #
        genParts = [l for l in Collection(event,"GenPart","nGenPart")]

        GenTopPt = -999
        GenAntiTopPt = -999
        TopPtWeight = 1.

        nGenTops = 0
        for i_part, genPart in enumerate(genParts):
            if genPart.pdgId ==  6:     GenTopPt = genPart.pt
            if genPart.pdgId == -6: GenAntiTopPt = genPart.pt
            
            if abs(genPart.pdgId) ==  6: nGenTops+=1

        if GenTopPt!=-999 and GenAntiTopPt!=-999 and nGenTops==2:
            SFTop     = exp(0.156    -0.00137*GenTopPt    )
            SFAntiTop = exp(0.156    -0.00137*GenAntiTopPt)
            TopPtWeight = sqrt(SFTop*SFAntiTop)


            
        ret    =  { 'GenTopPt'   : GenTopPt } #initialize the dictionary with a first entry
        ret['GenAntiTopPt'] = GenAntiTopPt
        ret['TopPtWeight']  = TopPtWeight
        return ret

if __name__ == '__main__':
    from sys import argv
    file = ROOT.TFile(argv[1])
    tree = file.Get("tree")
    class Tester(Module):
        def __init__(self, name):
            Module.__init__(self,name,None)
            self.sf = EventVars1LWeightsForSystematics()
        def analyze(self,ev):
            print "\nrun %6d lumi %4d event %d: leps %d" % (ev.run, ev.lumi, ev.evt, ev.nLepGood)
#            tree.Show(0)
            print self.sf(ev)
    el = EventLoop([ Tester("tester") ])
    el.loop([tree], maxEvents = 50)
