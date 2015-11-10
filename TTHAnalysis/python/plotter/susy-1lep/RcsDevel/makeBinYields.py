#!/usr/bin/env python
from CMGTools.TTHAnalysis.plotter.mcAnalysis import *
import sys, os, os.path

from searchBins import *
from math import hypot

# trees
#Tdir = "/nfs/dust/cms/group/susy-desy/Run2/ACDV/CMGtuples/MC/SPRING15/Spring15/Links/"
#FTdir = "/nfs/dust/cms/group/susy-desy/Run2/ACDV/CMGtuples/MC/SPRING15/Spring15/Links/Friends/"

#Tdir = "/afs/desy.de/user/l/lobanov/public/CMG/SampLinks_Spring15_25ns"
#mcFTdir = "/afs/desy.de/user/l/lobanov/public/CMG/SampLinks_Spring15_25ns/Friends/MC/ele_CBID_PUave70mb"
#dataFTdir = "/afs/desy.de/user/l/lobanov/public/CMG/SampLinks_Spring15_25ns/Friends/Data/ele_CBID_1p2fb"

Tdir = "/afs/desy.de/user/l/lobanov/public/CMG/SampLinks_MiniAODv2"
mcFTdir = "/afs/desy.de/user/l/lobanov/public/CMG/SampLinks_MiniAODv2/Friends/MC/eleCBID_SM_Signal"
sigFTdir = "/afs/desy.de/user/l/lobanov/public/CMG/SampLinks_MiniAODv2/Friends/MC/eleCBID_T1ttt_Scans"

# new data
dataFTdir = "/afs/desy.de/user/l/lobanov/public/CMG/SampLinks_MiniAODv2/Friends/Data/ele_CBID_1p5fb"

def addOptions(options):

    # LUMI (overwrite default 19/fb)
    if options.lumi > 19:
        options.lumi = 3
    else:
        options.lumi = 1.26

    # set tree options
    options.path = Tdir
    #options.friendTrees = [("sf/t",FTdir+"/evVarFriend_{cname}.root")]
    options.friendTreesMC = [("sf/t",mcFTdir+"/evVarFriend_{cname}.root")]
    options.friendTreesData = [("sf/t",dataFTdir+"/evVarFriend_{cname}.root")]
    options.tree = "treeProducerSusySingleLepton"

    # extra options
    options.doS2V = True
    options.weight = True
    options.final  = True
    options.allProcesses  = True
    #options.maxEntries = 1000

    # signal scan
    if options.signal:
        options.var =  "mLSP:mGo*(nEl-nMu)"
        #options.bins = "60,-1500,1500,30,0,1500"
        #options.bins = "34,-1700,1700,10,0,1500"
        options.bins = "161,-2012.5,2012.5,41,-25,2025.5"

        options.friendTrees = [("sf/t",sigFTdir+"/evVarFriend_{cname}.root")]
        options.cutsToAdd += [("base","Selected","Selected == 1")] # make always selected for signal

    elif options.grid:
        options.var =  "Selected:(nEl-nMu)"
        #options.bins = "2,-1.5,1.5,2,-1.5,1.5"
        options.bins = "3,-1.5,1.5,2,-1.5,1.5"

    elif options.plot:

        options.cutsToAdd += [("base","Selected","Selected == 1")] # make always selected for plots

        #options.var/bins must be setup by user
        if options.var == "LT":
            options.bins = "[250,350,450,600,1200]"
        elif options.var == "HT":
            options.bins = "[500,750,1000,1250,1600]"
            #options.bins = "25,500,1500"

def makeLepYieldGrid(hist, options):

    for ybin in range(1,hist.GetNbinsY()+1):
        ymu = hist.GetBinContent(1,ybin)
        yele = hist.GetBinContent(3,ybin)

        # set MC errors to be sqrt(N)
        if options.mcPoissonErrors:
            #print "Setting Poisson errors for MC"
            hist.SetBinError(1,ybin,sqrt(ymu))
            hist.SetBinError(3,ybin,sqrt(yele))

        ymuErr = hist.GetBinError(1,ybin)
        yeleErr = hist.GetBinError(3,ybin)

        ylep = ymu+yele
        ylepErr = hypot(ymuErr,yeleErr)

        hist.SetBinContent(2,ybin,ylep)
        hist.SetBinError(2,ybin,ylepErr)

        if options.verbose > 1:
            print 'Summary for', hist.GetName()
            print 'Mu yields:\t', ymu, ymuErr
            print 'Ele yields:\t', yele, yeleErr
            print 'Mu+Ele yields:\t', ylep, ylepErr

def makeUpHist(hist, options):

    hist.SetName(hist.GetName().replace('x_','')) # replace x_

    if options.grid:
        hist.SetStats(0)

        hist.GetXaxis().SetTitle("")
        hist.GetYaxis().SetTitle("")

        hist.GetXaxis().SetBinLabel(1,"mu")
        hist.GetXaxis().SetBinLabel(2,"mu+ele")
        hist.GetXaxis().SetBinLabel(3,"ele")

        hist.GetYaxis().SetBinLabel(1,"anti")
        hist.GetYaxis().SetBinLabel(2,"selected")

        makeLepYieldGrid(hist, options)

    if options.signal:
        hist.SetStats(0)

        hist.GetXaxis().SetTitle("m_{#tildeg}")
        hist.GetYaxis().SetTitle("m_{LSP}")

def writeYields(options):

    addOptions(options)

    if options.verbose > 1:
        print options

    # make MCA and cut vars
    mca  = MCAnalysis(options.mcaFile,options)
    cuts = CutsFile(options.cutFile,options)

    # make bin name and outdir names
    binname = options.bin
    if options.outdir == None:
        outdir = "test/"
    else:
        outdir = options.outdir

    # get report
    if options.pretend:
        report = []
    else:
        report = mca.getPlotsRaw("x", options.var, options.bins, cuts.allCuts(), nodata=options.asimov)

    # add sum MC entry
    if not options.pretend:
        totalMC = []; ewkMC = []
        for p in mca.listBackgrounds():
            if p in report and 'TTdiLep' not in p and 'TTsemiLep' not in p and 'TTincl' not in p:
            #if p in report and 'TTdiLep' not in p and 'TTsemiLep' not in p:
                print 'adding for background',p
                totalMC.append(report[p])
                if 'QCD' not in p:
                    print 'adding for ewk', p
                    ewkMC.append(report[p])

            report['x_background'] = mergePlots("x_background", totalMC)
            report['x_EWK'] = mergePlots("x_EWK", ewkMC)

    '''
    if options.asimov:
        tomerge = []
        for p in mca.listBackgrounds():
            if p in report: tomerge.append(report[p])
        report['data_obs'] = mergePlots(binname+"_data_obs", tomerge)
    #else:
    #    report['data_obs'] = report['data'].Clone(binname+"_data_obs")
    '''

    ydir = outdir+"/"
    if not os.path.exists(ydir): os.system("mkdir -p "+ydir)

    foutname = ydir+binname+".yields.root"
    workspace = ROOT.TFile.Open(foutname, "RECREATE")
    if options.verbose > 0:
        print 'Writing', foutname
        print 'Yields:'

    if not options.pretend:
        for n,h in report.iteritems():
            makeUpHist(h,options)

            if options.verbose > 0 and options.grid:
                print "\t%s (%8.3f selected events)" % (h.GetName(),h.GetBinContent(2,2))
            if options.verbose > 0 and options.signal:
                print "\t%s (%8.3f total events)" % (h.GetName(),h.Integral())

            workspace.WriteTObject(h,h.GetName())
    workspace.Close()

    return 1

def submitJobs(args, nchunks):

    # make unique name for jobslist
    import time
    itime = int(time.time())
    jobListName = 'jobList_%i.txt' %(itime)
    jobList = open(jobListName,'w')
    print 'Filling %s with job commands' % (jobListName)

    # not to run again
    if '-b' in args: args.remove('-b')

    # execute only one thread
    args += ['-j','1']

    for chunk in range(nchunks):
        chargs = args + ['-c',str(chunk)]
        runcmd = " ".join(str(arg) for arg in chargs )
        jobList.write(runcmd + '\n')

    # check log dir
    logdir = 'logs'
    if not os.path.exists(logdir): os.system("mkdir -p "+logdir)

    # submit job array on list
    subCmd = 'qsub -t 1-%s -o logs nafbatch_runner.sh %s' %(nchunks,jobListName)
    print 'Going to submit', nchunks, 'jobs with', subCmd
    os.system(subCmd)

    jobList.close()
    return 1

if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()

    parser.usage = '%prog [options]'
    parser.description="""
    Make yields from trees
    """

    addMCAnalysisOptions(parser)

    # extra options for tty
    parser.add_option("--mca", dest="mcaFile",default="mca-Spring15.txt",help="MCA sample list")
    parser.add_option("--cuts", dest="cutFile",default="trig_base.txt",help="Baseline cuts file")
    parser.add_option("--binname", dest="binname",default="test",help="Binname")

    # options for cards
    parser.add_option("--var", dest="var",default="1",help="Variable")
    parser.add_option("--bins", dest="bins",default="[0.5,1.5]",help="Histo Bins")

    # I/O options
    parser.add_option("-o",   "--out",    dest="outname", type="string", default=None, help="output name")
    parser.add_option("--od", "--outdir", dest="outdir", type="string", default=None, help="output name")

    # running options
    parser.add_option("-v","--verbose",  dest="verbose",  default=0,  type="int",    help="Verbosity level (0 = quiet, 1 = verbose, 2+ = more)")
    parser.add_option("--pretend", dest="pretend",default=False, action="store_true",help="pretend to do it")

    # batch options
    parser.add_option("-c","--chunk", dest="chunk",type="int",default=None,help="Number of chunk")
    parser.add_option("-b","--batch", dest="batch",default=False, action="store_true", help="batch command for submission")
    parser.add_option("--jobList","--jobList", dest="jobListName",default="jobList.txt",help="job list name")

    # more options
    parser.add_option("--asimov", dest="asimov", action="store_true", default=False, help="Make Asimov pseudo-data")
    parser.add_option("--mcPoisson", dest="mcPoissonErrors", action="store_true", default=False, help="Make MC errors poisson")
    parser.add_option("--signal", dest="signal", action="store_true", default=False, help="Is signal scan")
    parser.add_option("--grid", dest="grid", action="store_true", default=False, help="Plot 2d grid: ele/mu vs selected/anti")

    # make normal plots
    parser.add_option("--plot", dest="plot", action="store_true", default=False, help="Do normal plot")

    #parser.add_option("--dummy",  dest="dummyYieldsForZeroBkg", action="store_true", default=False, help="Set dummy yields such it corresponds to 0.01 for 4/fb");
    #parser.add_option("--ignoreEmptySignal",  dest="ignoreEmptySignal", action="store_true", default=False, help="Do not write out a datacard if the expected signal is less than 0.01");

    # Read options and args
    (options,args) = parser.parse_args()

    if options.verbose > 0 and len(args) > 0:
        print 'Arguments', args

    # make cut list
    cDict = {}

    cDict = cutDictCR
    cDict.update(cutDictSR)

    doNjet9 = False
    if doNjet9:
        cDict.update(cutDictSRf9)
        cDict.update(cutDictCRf9)

    #cDict = cutQCD #QCD
    #cDict = cutIncl #Inclusive

    # for LT/HT plots
    #cDict = cutLTbinsSR
    #cDict.update(cutLTbinsCR)

    binList = sorted(cDict.keys())

    if options.batch:
        print "Going to prepare batch jobs..."
        subargs =  sys.argv
        submitJobs(subargs, len(binList))
        exit(0)

    print "Beginning processing locally..."
    if options.chunk == None:
        # execute all bins locally
        for idx,bin in enumerate(binList):
            cuts = cDict[bin]
            options.bin = bin
            options.cutsToAdd = cuts

            if options.verbose > 0:
                print 80*'#'
                print 'Processing bin #%i/%i' %(idx,len(binList))
                print '%s with cuts' %(bin),
                for cut in cuts:
                    print cut[2],'+',
                print
            else:
                print '.',
            writeYields(options)
        print
    elif options.chunk < len(binList):
        # to test a single job
        bin = binList[options.chunk]
        idx = options.chunk

        cuts = cDict[bin]
        options.bin = bin
        options.cutsToAdd = cuts

        if options.verbose > 0:
            print 80*'#'
            print 'Processing chunk #%i/%i' %(idx,len(binList))
            print '%s with cuts' %(bin),
            for cut in cuts:
                print cut[2],'+',
            print
        else:
            print '.',
        writeYields(options)
    else:
        print "Nothing to process!"

    print 'Finished'
