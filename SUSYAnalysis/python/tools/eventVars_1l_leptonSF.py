from CMGTools.TTHAnalysis.treeReAnalyzer import *
import ROOT
import itertools
import PhysicsTools.Heppy.loadlibs

### SF ROOT files
eleSFname = "../python/tools/leptonSFs/eleSF.root"
eleHname = "CutBasedTight"
muSFname = "../python/tools/leptonSFs/muonSF.root"
muHname = "pt_abseta_PLOT_pair_probeMultiplicity_bin0_&_tag_combRelIsoPF04dBeta_bin0_&_tag_pt_bin0_&_tag_IsoMu20_pass"

hEleSF = 0
hMuSF = 0

# Load SFs
tf = ROOT.TFile(eleSFname,"READ")
hEleSF = tf.Get(eleHname).Clone()
hEleSF.SetDirectory(0)
tf.Close()
if not hEleSF:
    print "Could not load ele SF"
    exit(0)

tf = ROOT.TFile(muSFname,"READ")
hMuSF = tf.Get(muHname).Clone()
hMuSF.SetDirectory(0)
tf.Close()
if not hMuSF:
    print "Could not load mu SF"
    exit(0)

def getLepSF(lep):

    lepPt = lep.pt#lep.p4().Et()
    lepEta = abs(lep.eta)

    if(abs(lep.pdgId) == 13): hSF = hMuSF
    elif(abs(lep.pdgId) == 11): hSF = hEleSF
    else: return 1

    # fit pt to hist
    maxPt = hSF.GetXaxis().GetXmax()
    if lepPt > maxPt: lepPt = maxPt-0.1

    bin = hSF.FindBin(lepPt,lepEta)
    lepSF = hSF.GetBinContent(bin)
    lepSFerr = hSF.GetBinError(bin)

    #print lep, hSF, lepPt, lepEta, bin, lepSF
    if lepSF == 0:
        print "zero SF found!"
        print lepPt, lepEta, bin, lepSF, lepSFerr
        return 1

    return (lepSF,lepSFerr)

class EventVars1L_leptonSF:
    def __init__(self):
        self.branches = [ "lepSF","lepSFerr" ]

    def listBranches(self):
        return self.branches[:]

    def __call__(self,event,base):

        # output dict:
        ret = {}

        ret['lepSF'] = 1; ret['lepSFerr'] = 1

        # get some collections from initial tree
        leps = [l for l in Collection(event,"LepGood","nLepGood")]; nlep = len(leps)
        #jets = [j for j in Collection(event,"Jet","nJet")]; njet = len(jets)

        ####################################
        # import output from previous step #
        #base = keyvals
        ####################################
        if len(base.keys()) < 1: return ret # do nothing if base is empty

        # get selected leptons
        tightLeps = []
        tightLepsIdx = base['tightLepsIdx']
        tightLeps = [leps[idx] for idx in tightLepsIdx]
        nTightLeps = len(tightLeps)

        if nTightLeps == 0: return ret
        else:
            # take SF for leading lepton
            lep = tightLeps[0]
            (lepSF,lepSFerr) = getLepSF(lep)
            ret['lepSF'] = lepSF
            ret['lepSFerr'] = lepSFerr

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
