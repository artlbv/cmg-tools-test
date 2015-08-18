import PhysicsTools.HeppyCore.framework.config as cfg
from PhysicsTools.HeppyCore.framework.config import printComps
from PhysicsTools.HeppyCore.framework.heppy_loop import getHeppyOption

# Tau-tau analyzers
from CMGTools.H2TauTau.proto.analyzers.TauMuAnalyzer import TauMuAnalyzer
from CMGTools.H2TauTau.proto.analyzers.H2TauTauTreeProducerTauMu import H2TauTauTreeProducerTauMu
from CMGTools.H2TauTau.proto.analyzers.TauDecayModeWeighter import TauDecayModeWeighter
from CMGTools.H2TauTau.proto.analyzers.TauFakeRateWeighter import TauFakeRateWeighter
from CMGTools.H2TauTau.proto.analyzers.LeptonWeighter import LeptonWeighter
from CMGTools.H2TauTau.proto.analyzers.SVfitProducer import SVfitProducer

from CMGTools.H2TauTau.proto.samples.spring15.connector import httConnector

# common configuration and sequence
from CMGTools.H2TauTau.htt_ntuple_base_cff import commonSequence, genAna, dyJetsFakeAna, puFileData, puFileMC, eventSelector


# Get all heppy options; set via "-o production" or "-o production=True"

# production = True run on batch, production = False (or unset) run locally
production = getHeppyOption('production')
production = False

# mu-tau specific configuration settings

shift = None
syncntuple = True
computeSVfit = False
pick_events = False


# When ready, include weights from CMGTools.H2TauTau.proto.weights.weighttable

# mc_tauEffWeight_mc = 'effTau_muTau_MC_2012ABCDSummer13'
# mc_muEffWeight_mc = 'effMu_muTau_MC_2012ABCD'
# mc_tauEffWeight = 'effTau_muTau_Data_2012ABCDSummer13'
# mc_muEffWeight = 'effMu_muTau_Data_2012ABCDSummer13'

mc_tauEffWeight_mc = None
mc_muEffWeight_mc = None
mc_tauEffWeight = None
mc_muEffWeight = None

dyJetsFakeAna.channel = 'mt'

# Define mu-tau specific modules

tauMuAna = cfg.Analyzer(
    TauMuAnalyzer,
    name='TauMuAnalyzer',
    pt1=18,
    eta1=2.1,
    iso1=0.1,
    looseiso1=9999.,
    pt2=20,
    eta2=2.3,
    iso2=1.5,
    looseiso2=9999.,
    m_min=10,
    m_max=99999,
    dR_min=0.5,
    from_single_objects=True,
    verbose=False
)

tauDecayModeWeighter = cfg.Analyzer(
    TauDecayModeWeighter,
    name='TauDecayModeWeighter',
)

tauFakeRateWeighter = cfg.Analyzer(
    TauFakeRateWeighter,
    name='TauFakeRateWeighter'
)

tauWeighter = cfg.Analyzer(
    LeptonWeighter,
    name='LeptonWeighter_tau',
    effWeight=None,
    effWeightMC=None,
    lepton='leg2',
    verbose=False,
    disable=True,
)

muonWeighter = cfg.Analyzer(
    LeptonWeighter,
    name='LeptonWeighter_mu',
    effWeight=None,
    effWeightMC=None,
    lepton='leg1',
    verbose=False,
    disable=True,
    idWeight=None,
    isoWeight=None
)

treeProducer = cfg.Analyzer(
    H2TauTauTreeProducerTauMu,
    name='H2TauTauTreeProducerTauMu'
)

syncTreeProducer = cfg.Analyzer(
    H2TauTauTreeProducerTauMu,
    name='H2TauTauSyncTreeProducerTauMu',
    varStyle='sync',
    # skimFunction='event.isSignal'
)

svfitProducer = cfg.Analyzer(
    SVfitProducer,
    name='SVfitProducer',
    # integration='VEGAS',
    integration='MarkovChain',
    # verbose=True,
    # order='21', # muon first, tau second
    l1type='tau',
    l2type='muon'
)

###################################################
### CONNECT SAMPLES TO THEIR ALIASES AND FILES  ###
###################################################
# my_connect = httConnector('TAUMU_743_TEST1', 'htautau_group',
#                           '.*root', 'mt', production=production, 
#                           splitFactor=1e5)
# my_connect.connect()
# MC_list = my_connect.MC_list

from CMGTools.RootTools.utils.splitFactor import splitFactor
from CMGTools.TTHAnalysis.samples.ComponentCreator import ComponentCreator
from CMGTools.TTHAnalysis.samples.samples_13TeV_74X import TTJets_LO, DYJetsToLL_M50, WJetsToLNu
from CMGTools.H2TauTau.proto.samples.spring15.triggers_tauMu  import mc_triggers as mc_triggers_mt

creator = ComponentCreator()
ggh160 = creator.makeMCComponent("GGH160", "/SUSYGluGluToHToTauTau_M-160_TuneCUETP8M1_13TeV-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/MINIAODSIM", "CMS", ".*root", 1.0)

MC_list = [ggh160, TTJets_LO, DYJetsToLL_M50, WJetsToLNu]


first_data = cfg.DataComponent(
    name='first2pb',
    intLumi='2.0', # in pb
    files=['/afs/cern.ch/user/g/gpetrucc/public/miniAOD-express_PAT_251168.root'],
    triggers=mc_triggers_mt,
    json=None
)


split_factor = 1e5

for sample in MC_list:
    sample.triggers = mc_triggers_mt
    sample.splitFactor = splitFactor(sample, split_factor)



data_list = [first_data]

###################################################
###              ASSIGN PU to MC                ###
###################################################
for mc in MC_list:
    mc.puFileData = puFileData
    mc.puFileMC = puFileMC

###################################################
###             SET COMPONENTS BY HAND          ###
###################################################
selectedComponents = MC_list + data_list
# selectedComponents = mc_dict['HiggsGGH125']
# for c in selectedComponents : c.splitFactor *= 5

###################################################
###                  SEQUENCE                   ###
###################################################
sequence = commonSequence
sequence.insert(sequence.index(genAna), tauMuAna)
sequence.append(tauDecayModeWeighter)
sequence.append(tauFakeRateWeighter)
sequence.append(tauWeighter)
sequence.append(muonWeighter)
if computeSVfit:
    sequence.append(svfitProducer)
sequence.append(treeProducer)
if syncntuple:
    sequence.append(syncTreeProducer)

###################################################
###             CHERRY PICK EVENTS              ###
###################################################

if pick_events:
    eventSelector.toSelect = [456471,47173,157585,147731,210457,432728,371706,364607,157184,165203,182572,240489,269584,307460,326678,328122,353889,376943,112525,113692,491647]
    sequence.insert(0, eventSelector)

###################################################
###            SET BATCH OR LOCAL               ###
###################################################
if not production:
    cache = True
    # comp = my_connect.mc_dict['HiggsSUSYGG160']
    # selectedComponents = [comp]
    # comp = selectedComponents[0]
    comp = TTJets_LO
    selectedComponents = [comp]
    comp.splitFactor = 1
    comp.fineSplitFactor = 1
    # comp.files = comp.files[]


# the following is declared in case this cfg is used in input to the
# heppy.py script
from PhysicsTools.HeppyCore.framework.eventsfwlite import Events
config = cfg.Config(components=selectedComponents,
                    sequence=sequence,
                    services=[],
                    events_class=Events
                    )

printComps(config.components, True)

while len(sequence)<2: sequence.pop()

def modCfgForPlot(config):
    config.components = []
