##########################################################
##       CONFIGURATION FOR SUSY SingleLep TREES       ##
## skim condition: >= 1 loose leptons, no pt cuts or id ##
##########################################################
import PhysicsTools.HeppyCore.framework.config as cfg

#Load all analyzers
from CMGTools.TTHAnalysis.analyzers.susyCore_modules_cff import *

#JSON
jsonAna.useLumiBlocks = True

####### Leptons  #####
# lep collection
lepAna.packedCandidates = 'packedPFCandidates'

## ELECTRONS
lepAna.loose_electron_pt  = 10
eleID = "CBID"

if eleID == "CBID":
	lepAna.loose_electron_id  = "POG_Cuts_ID_SPRING15_25ns_v1_ConvVetoDxyDz_Veto_full5x5"
	lepAna.loose_electron_lostHits = 999. # no cut since embedded in ID
	lepAna.loose_electron_dxy    = 999. # no cut since embedded in ID
	lepAna.loose_electron_dz     = 999. # no cut since embedded in ID

	lepAna.inclusive_electron_id  = "" # Keep no ID
	lepAna.inclusive_electron_lostHits = 5. #
	lepAna.inclusive_electron_dxy    = 0.5 # very loose (like in core)
	lepAna.inclusive_electron_dz     = 1.0 # very loose (like in core)

elif eleID == "MVAID":
	inclusive_electron_id  = "" # same as in susyCore

	#lepAna.loose_electron_id = "POG_MVA_ID_Phys14_NonTrig_VLoose" # Phys14 era
	lepAna.loose_electron_id = "POG_MVA_ID_Spring15_NonTrig_VLoose" # Spring15 25ns era

elif eleID == "Incl": # as inclusive as possible
	lepAna.loose_electron_id  = ""
	lepAna.loose_electron_lostHits = 999. # no cut
	lepAna.loose_electron_dxy    = 999.
	lepAna.loose_electron_dz     = 999.

	lepAna.inclusive_electron_id  = ""
	lepAna.inclusive_electron_lostHits = 999.  # no cut
	lepAna.inclusive_electron_dxy    = 999. # no cut since embedded in ID
	lepAna.inclusive_electron_dz     = 999. # no cut since embedded in ID

## MUONS
lepAna.loose_muon_pt  = 10

# Isolation
isolation = "miniIso"

if isolation == "miniIso":
	# do miniIso
	lepAna.doMiniIsolation = True
	lepAna.miniIsolationPUCorr = 'rhoArea'
	lepAna.miniIsolationVetoLeptons = None
	lepAna.loose_muon_isoCut     = lambda muon : muon.miniRelIso < 0.4
	lepAna.loose_electron_isoCut = lambda elec : elec.miniRelIso < 0.4
elif isolation == "relIso03":
	# normal relIso03
	lepAna.ele_isoCorr = "rhoArea"
	lepAna.mu_isoCorr = "rhoArea"

	lepAna.loose_electron_relIso = 0.5
	lepAna.loose_muon_relIso = 0.5

# --- LEPTON SKIMMING ---
ttHLepSkim.minLeptons = 0
ttHLepSkim.maxLeptons = 999
#LepSkim.idCut  = ""
#LepSkim.ptCuts = []

####### JETS #########
jetAna.jetPt = 30
jetAna.jetEta = 2.4

# --- JET-LEPTON CLEANING ---
jetAna.cleanSelectedLeptons = True
if jetAna.cleanSelectedLeptons:	jetAna.minLepPt = 10

## JEC -- see preprocessor for MET
#use default for 25 ns from susycore Summer15_25nsV2_MC
#jetAna.mcGT = "Summer15_50nsV4_MC"
#jetAna.dataGT = "Summer15_50nsV4_DATA"

jetAna.doQG = True
jetAna.smearJets = False #should be false in susycore, already
jetAna.recalibrateJets = True #should be true in susycore, already

## MET -- check preprocessor
metAna.recalibrate = False #should be false in susycore, already

## Iso Track
isoTrackAna.setOff=False

# store all taus by default
genAna.allGenTaus = True

########################
###### ANALYZERS #######
########################

#add LHE ana for HT info
from PhysicsTools.Heppy.analyzers.gen.LHEAnalyzer import LHEAnalyzer
LHEAna = LHEAnalyzer.defaultConfig

from CMGTools.TTHAnalysis.analyzers.ttHLepEventAnalyzer import ttHLepEventAnalyzer
ttHEventAna = cfg.Analyzer(
	ttHLepEventAnalyzer, name="ttHLepEventAnalyzer",
	minJets25 = 0,
	)

## Insert the FatJet, SV, HeavyFlavour analyzers in the sequence
susyCoreSequence.insert(susyCoreSequence.index(ttHCoreEventAna),
			ttHFatJetAna)
susyCoreSequence.insert(susyCoreSequence.index(ttHCoreEventAna),
			ttHSVAna)

## Single lepton + ST skim
from CMGTools.TTHAnalysis.analyzers.ttHSTSkimmer import ttHSTSkimmer
ttHSTSkimmer = cfg.Analyzer(
	ttHSTSkimmer, name='ttHSTSkimmer',
	minST = 200,
	)

## HT skim
from CMGTools.TTHAnalysis.analyzers.ttHHTSkimmer import ttHHTSkimmer
ttHHTSkimmer = cfg.Analyzer(
	ttHHTSkimmer, name='ttHHTSkimmer',
	minHT = 350,
	)

#from CMGTools.RootTools.samples.triggers_13TeV_Spring15 import * # central trigger list
from CMGTools.RootTools.samples.triggers_13TeV_Spring15_1l import *

triggerFlagsAna.triggerBits = {
	## hadronic
	'HT350' : triggers_HT350,
	'HT600' : triggers_HT600,
	'HT800' : triggers_HT800,
	'MET170' : triggers_MET170,
	'HT350MET120' : triggers_HT350MET120,
	'HT350MET100' : triggers_HT350MET100,
	'HTMET' : triggers_HT350MET100 + triggers_HT350MET120,
	## muon
	'SingleMu' : triggers_1mu,
	'IsoMu27' : triggers_1mu,
	'IsoMu20' : triggers_1mu20,
	'Mu45eta2p1' : trigger_1mu_noiso_r,
	'Mu50' : trigger_1mu_noiso_w,
	'MuHT600' : triggers_mu_ht600,
	'MuHT400MET70' : triggers_mu_ht400_met70,
	'MuHT350MET70' : triggers_mu_ht350_met70,
	'MuHT350MET50' : triggers_mu_ht350_met50,
	'MuHT350' : triggers_mu_ht350,
	'MuHTMET' : triggers_mu_ht350_met70 + triggers_mu_ht400_met70,
	'MuMET120' : triggers_mu_met120,
	'MuHT400B': triggers_mu_ht400_btag,
	## electrons
	'IsoEle32' : triggers_1el,
	'IsoEle23' : triggers_1el23,
	'IsoEle22' : triggers_1el22,
	'Ele105' : trigger_1el_noiso,
	'EleHT600' : triggers_el_ht600,
	'EleHT400MET70' : triggers_el_ht400_met70,
	'EleHT350MET70' : triggers_el_ht350_met70,
	'EleHT350MET50' : triggers_el_ht350_met50,
	'EleHT350' : triggers_el_ht350,
	'EleHTMET' : triggers_el_ht350_met70 + triggers_el_ht400_met70,
	'EleHT200' :triggers_el_ht200,
	'EleHT400B': triggers_el_ht400_btag
	}

#-------- SAMPLES AND TRIGGERS -----------

#-------- HOW TO RUN
isData = True # default, but will be overwritten below

sample = 'MC'
#sample = 'data'
test = 1

if sample == "MC":

	print 'Going to process MC'

	jecDBFile = '$CMSSW_BASE/src/CMGTools/RootTools/data/jec/Summer15_25nsV2_MC.db'
	jecEra    = 'Summer15_25nsV2_MC'

	isData = False

	# modify skim
	ttHLepSkim.minLeptons = 1

	# -- new 74X samples
#	from CMGTools.RootTools.samples.samples_13TeV_74X import *
	# -- samples at DESY
	from CMGTools.SUSYAnalysis.samples.samples_13TeV_74X_desy import *

	# select components
	selectedComponents = [
		TTJets_LO_25ns,
	]

	if test==1:
		# test a single component, using a single thread.
		#comp = TTJets_LO_25ns
		comp = T1tttt_mGo_1500to1525_mLSP_50to1125
		comp.files = comp.files[:1]
		selectedComponents = [comp]
		comp.splitFactor = 1
	elif test==2:
		# test all components (1 thread per component).
		for comp in selectedComponents:
			comp.splitFactor = 1
			comp.fineSplitFactor = 2
			comp.files = comp.files[:1]
	elif test==3:
		# run all components (1 thread per component).
		for comp in selectedComponents:
			comp.fineSplitFactor = 2
			comp.splitFactor = len(comp.files)
	elif test==0:
		# PRODUCTION
		# run on everything

		#selectedComponents =[ TTJets_LO_25ns ]
		#selectedComponents = [ TTJets_HT600to800 , TTJets_HT800to1200, TTJets_HT1200to2500, TTJets_HT2500toInf] + WJetsToLNuHT + QCD_HT + TTV + DYJetsM50HT
		#selectedComponents += [TTJets_SingleLeptonFromT_ext1 , TTJets_SingleLeptonFromTbar_ext1 , TTJets_DiLepton_ext1]
		#selectedComponents = [TTJets_DiLepton]
		#selectedComponents = [TTJets_DiLepton_ext1]
		selectedComponents = [ T1tttt_mGo_1500to1525_mLSP_50to1125 ]

		for comp in selectedComponents:
			comp.fineSplitFactor = 2
			comp.splitFactor = len(comp.files)

elif sample == "data":

	print 'Going to process DATA'

	jecDBFile = '$CMSSW_BASE/src/CMGTools/RootTools/data/jec/Summer15_25nsV5_DATA.db'
	jecEra    = 'Summer15_25nsV5_DATA'

	isData = True

	# modify skim
	ttHLepSkim.minLeptons = 0

	# central samples
#	from CMGTools.RootTools.samples.samples_13TeV_DATA2015 import *
	# samples at DESY
	from CMGTools.SUSYAnalysis.samples.samples_13TeV_DATA2015_desy import *

	#selectedComponents = [ SingleElectron_Run2015B, SingleMuon_Run2015B ]
	#selectedComponents = [ SingleElectron_Run2015B ]
	#selectedComponents = [ SingleElectron_Run2015B, SingleElectron_Run2015B_17Jul ]
	#selectedComponents = [ SingleMuon_Run2015B, SingleMuon_Run2015B_17Jul ]
	#selectedComponents = [ JetHT_Run2015B, JetHT_Run2015B_17Jul ]
	#selectedComponents = [ HTMHT_Run2015B ]

	selectedComponents = [ JetHT_Run2015D ] #, SingleElectron_Run2015D, SingleMuon_Run2015D ]
	#selectedComponents = [ SingleElectron_Run2015D, SingleMuon_Run2015D ]

	if test!=0 and jsonAna in susyCoreSequence: susyCoreSequence.remove(jsonAna)

	if test==1:
		# test a single component, using a single thread.
		#comp = SingleMuon_Run2015D
		#comp = JetHT_Run2015D
		comp = SingleElectron_Run2015D
		#comp.files = ['dcap://dcache-cms-dcap.desy.de/pnfs/desy.de/cms/tier2//store/data/Run2015D/JetHT/MINIAOD/PromptReco-v3/000/256/587/00000/F664AC07-935D-E511-A019-02163E01424B.root']
		comp.files = comp.files[20:30]
		#comp.files = comp.files[:1]
		selectedComponents = [comp]
#		comp.splitFactor = 1
		comp.splitFactor = len(comp.files)
	elif test==2:
		# test all components (1 thread per component).
		for comp in selectedComponents:
			comp.splitFactor = 1
			comp.fineSplitFactor = 2
			comp.files = comp.files[:1]
	elif test==3:
		# run all components (10 files per component).
		for comp in selectedComponents:
			comp.files = comp.files[20:30]
			comp.fineSplitFactor = 2
			comp.splitFactor = len(comp.files)
	elif test==0:
		# PRODUCTION
		# run on everything
		for comp in selectedComponents:
			comp.fineSplitFactor = 2
			comp.splitFactor = len(comp.files)



removeResiduals = False

# use consistent JEC residuals for MET and Jets
if removeResiduals:
	jetAna.applyL2L3Residual = False
else:
	jetAna.applyL2L3Residual = True

# -------------------- Running pre-processor
preprocessor = None
doMETpreprocessor = True
if doMETpreprocessor:
	import tempfile
	import subprocess
	tempfile.tempdir=os.environ['CMSSW_BASE']+'/tmp'
	tfile, tpath = tempfile.mkstemp(suffix='.py',prefix='MET_preproc_')
	os.close(tfile)
	extraArgs=[]
	if isData:
		extraArgs.append('--isData')
		GT= '74X_dataRun2_Prompt_v1'
	else:
		GT= 'MCRUN2_74_V9A'
	if removeResiduals:extraArgs.append('--removeResiduals')
	args = ['python',
		os.path.expandvars('$CMSSW_BASE/python/CMGTools/ObjectStudies/corMETMiniAOD_cfgCreator.py'),\
			'--GT='+GT,
		'--outputFile='+tpath,
		'--jecDBFile='+jecDBFile,
		'--jecEra='+jecEra
		] + extraArgs
#print "Making pre-processorfile:"
#print " ".join(args)
	subprocess.call(args)
	staticname = "$CMSSW_BASE/tmp/MetType1_jec_%s.py"%(jecEra)
	import filecmp
	if os.path.isfile(staticname) and filecmp.cmp(tpath,staticname):
		os.system("rm %s"%tpath)
	else:
		os.system("mv %s %s"%(tpath,staticname))
	preprocessorFile = staticname
	from PhysicsTools.Heppy.utils.cmsswPreprocessor import CmsswPreprocessor
	preprocessor = CmsswPreprocessor(preprocessorFile)

#--------- Tree Producer
from CMGTools.TTHAnalysis.analyzers.treeProducerSusySingleLepton import *
treeProducer = cfg.Analyzer(
	AutoFillTreeProducer, name='treeProducerSusySingleLepton',
	vectorTree = True,
	saveTLorentzVectors = False,  # can set to True to get also the TLorentzVectors, but trees will be bigger
	defaultFloatType = 'F', # use Float_t for floating point
	PDFWeights = PDFWeights,
	globalVariables = susySingleLepton_globalVariables,
	globalObjects = susySingleLepton_globalObjects,
	collections = susySingleLepton_collections,
	)

## TEMPORARY
# HBHE filter analyzer
from CMGTools.TTHAnalysis.analyzers.hbheAnalyzer import hbheAnalyzer
hbheFilterAna = cfg.Analyzer(
    hbheAnalyzer, name = 'hbheAnalyzer',IgnoreTS4TS5ifJetInLowBVRegion=False
)

#-------- SEQUENCE

sequence = cfg.Sequence(susyCoreSequence+[
		LHEAna,
		ttHEventAna,
		#ttHSTSkimmer,
		ttHHTSkimmer,
		hbheFilterAna,
		treeProducer,
		])

# remove skimming for Data
if isData:
	sequence.remove(ttHHTSkimmer)
#	sequence.remove(ttHSTSkimmer)

from PhysicsTools.HeppyCore.framework.eventsfwlite import Events
config = cfg.Config( components = selectedComponents,
		     sequence = sequence,
		     services = [],
		     preprocessor=preprocessor,
		     events_class = Events)
