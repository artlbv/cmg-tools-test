##########################################################
##       CONFIGURATION FOR HZZ4L TREES                  ##
##########################################################
import PhysicsTools.HeppyCore.framework.config as cfg

#Load all analyzers
from CMGTools.HToZZ4L.analyzers.hzz4lCore_modules_cff import * 
from CMGTools.HToZZ4L.analyzers.TwoLeptonAnalyzer import TwoLeptonAnalyzer

twoLeptonAnalyzer = cfg.Analyzer(
    TwoLeptonAnalyzer, name="twoLeptonAnalyzer",
    #attachFsrToGlobalClosestLeptonOnly = True
)

twoLeptonEventSkimmer = cfg.Analyzer(
    FourLeptonEventSkimmer, name="twoLeptonEventSkimmer",
    required = ['bestIsoZ']
)


twoLeptonTreeProducer = cfg.Analyzer(
     AutoFillTreeProducer, name='twoLeptonTreeProducer',
     vectorTree = False,
     saveTLorentzVectors = False,  # can set to True to get also the TLorentzVectors, but trees will be bigger
     globalVariables = hzz_globalVariables, # rho, nvertices, njets
     globalObjects = hzz_globalObjects, # met
     collections = {
         "bestIsoZ"        : NTupleCollection("z",   ZType, 1, help="Four Lepton Candidates"),    
         "selectedLeptons" : NTupleCollection("Lep", leptonTypeHZZ, 10, help="Leptons after the preselection"),
         "cleanJets"       : NTupleCollection("Jet", jetTypeExtra, 10, help="Cental jets after full selection and cleaning, sorted by pt"),
         "fsrPhotonsNoIso" : NTupleCollection("FSR", fsrPhotonTypeHZZ, 10, help="Photons for FSR recovery (isolation not applied)"),
     },
     defaultFloatType = 'F',
)


#-------- SEQUENCE
sequence = cfg.Sequence([
    skimAnalyzer,
    genAna,
    jsonAna,
    triggerAna,
    pileUpAna,
    vertexAna,
    lepAna,
    eleMuClean,
    jetAna,
    metAna,
    triggerFlagsAna,
    fsrPhotonMaker,
    twoLeptonAnalyzer, 
    twoLeptonEventSkimmer, 
    twoLeptonTreeProducer 
])

#-------- SAMPLES AND TRIGGERS -----------
from CMGTools.HToZZ4L.samples.samples_13TeV_Spring15 import *
selectedComponents = mcSamples + dataSamples
selectedComponents = [ DYJetsToLL_M50, SingleMu_742 ]
for comp in mcSamples:
    comp.triggers = triggers_1mu_iso
    comp.vetoTriggers = []

from PhysicsTools.HeppyCore.framework.heppy_loop import getHeppyOption
test = getHeppyOption('test')
if test == "1":
    comp = DYJetsToLL_M50
    comp.files = comp.files[:1]
    comp.splitFactor = 1
    comp.fineSplitFactor = 1 if getHeppyOption('single') else 5
    selectedComponents = [ comp ]
    if getHeppyOption('events'):
        eventSelector.toSelect = [ eval("("+x.replace(":",",")+")") for x in getHeppyOption('events').split(",") ]
        sequence = cfg.Sequence([eventSelector] + hzz4lCoreSequence)
        print "Will select events ",eventSelector.toSelect
elif test == '2':
    for comp in selectedComponents:
        comp.files = comp.files[:1]
        comp.splitFactor = 1
        comp.fineSplitFactor = 1
elif test == '3':
    for comp in selectedComponents:
        comp.files = comp.files[:1]
        comp.splitFactor = 1
        comp.fineSplitFactor = 3


# the following is declared in case this cfg is used in input to the heppy.py script
from PhysicsTools.HeppyCore.framework.eventsfwlite import Events
config = cfg.Config( components = selectedComponents,
                     sequence = sequence,
                     services = [],  
                     events_class = Events)


