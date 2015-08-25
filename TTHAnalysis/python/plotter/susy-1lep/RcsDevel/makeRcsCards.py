#!/usr/bin/python

#import sys
#import os

#import searchBins, runFuncs
from runFuncs import *
from searchBins import *

def getJobList():
    import time
    itime = int(time.time())
    jobListName = 'jobList_%i.txt' %(itime)

    return jobListName


## These must be defined as standalone functions, to allow runing them in parallel
Tdir = "/nfs/dust/cms/group/susy-desy/Run2/ACDV/CMGtuples/MC/SPRING15/Spring15/Links"
FTdir = "/nfs/dust/cms/group/susy-desy/Run2/ACDV/CMGtuples/MC/SPRING15/Spring15/Links/Friends"

def _makeCard(options):

    print 80*'#'
    print 'Going to create cards root files"'

    if options.batch:
        if options.jobListName != "jobList.txt":
            # make unique name for jobslist
            jobListName = getJobList()
            jobList = open(jobListName,'w')
            print 'Filling %s with job commands' % (jobListName)

            # submit job array on list
            #subCmd = 'qsub -t 1-%s -o logs nafbatch_runner.sh %s' %(len(jobs),jobListName)
            #print 'Going to submit', len(jobs), 'jobs with', subCmd
            #args=subCmd.split()
            #subprocess.call(args) #will run immediately
            jobList.close()


    #args = (options.lumi,options.jobs,Tdir,FTdir,options.outdir)
    cuts =  ' -R "HT HT500 HT>500"' #temp
    cutName = "CnC_test"

    args = (options, Tdir, FTdir, cuts, cutName)

    makeCard(args)

    print 80*'#'
    print 'Finished'

    return 1

if __name__ == "__main__":

    from optparse import OptionParser
    parser = OptionParser()

    parser.usage = '%prog <target_directories> [options]'
    parser.description="""
    Make cards for Rcs
    """

    parser.add_option("-o","--outdir", dest="outdir",default="test", help="out dir for cards")
    parser.add_option("-j","--jobs", dest="jobs",default=8, help="number of threads")
    parser.add_option("-l","--lumi", dest="lumi",default=3.0, help="lumi")
    parser.add_option("-b","--batch", dest="batch",default=False, action="store_true", help="batch command for submission")
    parser.add_option("--jobList","--jobList", dest="jobListName",default="jobList.txt", , help="job list name")
    parser.add_option("-v","--verbose", dest="verbose",default=False, action="store_true",help="verbose output")
    parser.add_option("-p","--pretend", dest="pretend",default=False, action="store_true",help="pretend to do it")
    parser.add_option("-f","--force", dest="force",default=False, action="store_true",help="force mode")

    (options,args) = parser.parse_args()

    if len(args)==0:
        #print 'provide at least one directory in argument. Use -h to display help'
        #print options, args
        _makeCard(options)
    else:
        _makeCard(options)
