#!/usr/bin/env python

import os
'''
from math import *
import re
import os, os.path
from array import array
'''

## safe batch mode
import sys
args = sys.argv[:]
sys.argv = ['-b']
import ROOT
sys.argv = args
ROOT.gROOT.SetBatch(True)

## OPTIONS

# exe line
#"python $PLOTDIR/makeShapeCardsSusy.py $PLOTDIR/$McaFile $PLOTDIR/susy-1lep/$CutFlowCard "$EXPR" "$BINS" $SYSTS -o $OUT $GO --dummyYieldsForZeroBkg;"

# settings
plotdir = "/afs/desy.de/group/cms/pool/lobanov/SUSY/Run2/CMG/Development/CMSSW_7_4_7_patch2/src/CMGTools/TTHAnalysis/python/plotter/"
rcsdir = "/afs/desy.de/group/cms/pool/lobanov/SUSY/Run2/CMG/Development/CMSSW_7_4_7_patch2/src/CMGTools/TTHAnalysis/python/plotter/susy-1lep/RcsDevel/"
shapeExe = "makeShapeCardsSusy.py"
# choose CF and MCA files
cutFlowCard = "cards_cf.txt"
mcaFile = "mca-Cards_test.txt"
#mcaFile = "mca-PAS.txt"

SYSTS="susyDummy.txt"
CnC_expr="1" #not used as of now
CnC_bins="[0.5,1.5]"

def makeCard(args):

    #(lumi,jobs,tdir,fdir,odir) = args
    (opt,tdir,fdir,cuts,cutName) = args
    lumi = opt.lumi
    jobs = opt.jobs
    odir = opt.outdir

    # main options
    #cmd = "python %s/makeShapeCardsSusy.py %s %s " % (plotdir, rcsdir + mcaFile, rcsdir + cutFlowCard)
    cmd = "python %s/makeShapeCardsSusy.py %s %s " % (plotdir, mcaFile, cutFlowCard)
    cmd += " %s %s %s " %(CnC_expr, CnC_bins, SYSTS)
    cmd += " -o %s.txt " % cutName

    # execution options
    exeopt = " -f --s2v --tree treeProducerSusySingleLepton --asimov  --od %s " %(odir)
    exeopt += " -j %i -l %f " %(jobs,lumi)
    exeopt += " -P %s -F sf/t %s/evVarFriend_{cname}.root " % (tdir,fdir)

    #print exeopt
    cmd += exeopt

    # cut name
    cmd += cuts

    # set dummy yields
    cmd += " --dummyYieldsForZeroBkg"

    if opt.pretend:
        print cmd
    elif opt.batch:
        jobList = open(opt.jobListName,'a')
        jobList.write(cmd+'\n')
        jobList.close()
    else:
        # execute locally
        os.system(cmd)

    return 1
