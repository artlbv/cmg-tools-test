#!/bin/env python

import sys
import re
import os
import pprint
import glob


def doold():

    for d in dirs:
        if not os.path.isdir(d):
            continue
        if d.find('_Chunk') == -1:
            continue
        logName  = '/'.join([d, 'log.txt'])
        if not os.path.isfile( logName ):
            print d, ': log.txt does not exist'
            badDirs.append(d)
            continue
        logFile = open(logName)
        nEvents = -1
        for line in logFile:
            try:
                nEvents = line.split('processed:')[1]
            except:
                pass
        if nEvents == -1:
            print d, 'cannot find number of processed events'
        elif nEvents == 0:
            print d, '0 events'
        else:
            #everything ok so far
            if options.checkCopy:
                match = ["*.txt", "*.log","*.out", "STD_OUTPUT"] if options.logfile == "" else [options.logfile]
                logNames = []
                for m in match:
                    logNames += glob.glob(d+"/"+m)
                succeeded = False
                for logName in logNames:
                    if not os.path.isfile( logName ):
                        print logName, 'does not exist'
                    else:
                        logFile = open(logName)
                        isRemote = False
                        for line in logFile:
                            if "gfal-copy" in line:
                                isRemote = True
                            if "copy succeeded" in line and "echo" not in line:
                                if not isRemote or "remote" in line:
                                    succeeded = True
                                    break
                                else:
                                    print logName, ': remote copy failed. Copied locally'
                    if succeeded:
                        break
                if succeeded:
                    continue # all good
                if logNames == []:
                    print d, ": no log files found matchig", match
                else:
                    print logNames, ': copy failed or not sent to the expected location'
            else:
                continue # all good
        badDirs.append(d)

    print 'list of bad directories:'
    pprint.pprint(badDirs)

    if options.batch is not None:
        for d in badDirs:
            oldPwd = os.getcwd()
            os.chdir( d )
            cmd =  [options.batch, '-J', d, ' < batchScript.sh' ]
            print 'resubmitting in', os.getcwd()
            cmds = ' '.join( cmd )
            print cmds
            os.system( cmds )
            os.chdir( oldPwd )

def getFlagDirs(sdir,flagName):

    dirList = []

    for flag in glob.glob(sdir+'/*Chunk*/'+flagName):
        dname = os.path.dirname(flag)
        dirList.append(dname)

    return dirList

def cleanUpDir(sdir, options = []):
    # Will check for processed/ing/failed flags in dir
    import glob, shutil

    print '#Going to check flags in', sdir

    # flag file names
    fproced = 'processed'; doneList = getFlagDirs(sdir, fproced)
    fprocing = 'processing'; runList = getFlagDirs(sdir, fprocing)
    ffailed = 'failed'; failList = getFlagDirs(sdir, ffailed)

    print '##Found chunks:',
    print '\tprocessed:%i' % len(doneList),
    print '\tprocessing:%i' % len(runList),
    print '\tfailed:%i' % len(failList),
    print '\ttotal:%i' % len(doneList+runList+failList)
    print 80*'#'

    # deal with finished jobs
    if len(doneList) > 0:
        # create processed dir
        procdir = os.path.join(sdir,fproced)

        if not os.path.isdir(procdir):
            if options.verbose:
                print 'Creating', procdir
            os.mkdir(procdir)

        # move processed chunks
        for chunkdir in doneList:
            chunkname = os.path.basename(chunkdir)
            if options.verbose:
                print 'Moving %s to %s' %(chunkdir,os.path.join(procdir,chunkname))
            if not options.pretend:
                shutil.move(chunkdir,os.path.join(procdir,chunkname))
        print 'Chunks ready for hadd!'

    # deal with processing jobs
    if len(runList) > 0:
        answ = []

        if not options.force:
            while ('y' not in answ and 'n' not in answ):
                ask = raw_input('Proceed with running chunks? [y/n]')
                answ.append(ask)

        if 'n' in answ:
            print 'Skipping running dirs'
        elif 'y' in answ:
            print "Deal with dirs with dirs labeled 'processing'."
            print "To Do"

    # deal with failed jobs
    if len(failList) > 0:

        for chunkdir in failList:
            chunkname = os.path.basename(chunkdir)

            # move looper log to fail
            looplog = os.path.join(chunkdir,'looper.log')
            loopdir = glob.glob(looplog)
            if loopdir != []:
                loopdir = []
                faildir = glob.glob(chunkdir+'/Loop_failed_*')[0]

                if options.verbose:
                    print loopdir, faildir
                    print 'Moving %s to %s' %(looplog,faildir+'/looper.log')
                if not options.pretend:
                    shutil.move(looplog,faildir+'/looper.log')

        # create command for resubmit
        subCmd = 'qsub -t 1-NJOBS -N JOBNAME BATCHSH'
        # number of jobs
        subCmd = subCmd.replace('NJOBS',str(len(failList)))
        # job names
        dirname = os.path.basename(sdir[:len(sdir)-1])
        dirname = dirname.replace('/','')
        subCmd = subCmd.replace('JOBNAME','Re'+dirname)
        # batch script
        batchScr = glob.glob(sdir+'batchScript.sh')
        subCmd = subCmd.replace('BATCHSH',str(batchScr[0]))

        if options.pretend:
            print 'Submit command:'
            print subCmd
        else:
            print 'Submitting jobs...'
            print subCmd
            #os.system(subCmd) # FIXME

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()

    parser.usage = '%prog <target_directories> [options]'
    parser.description="""
    Check one or more chunck folders.
    Wildcard (*) can be used to specify multiple directories
    """

    parser.add_option("-b","--batch", dest="batch",
                      default=None, help="batch command for resubmission")
    parser.add_option("-v","--verbose", dest="verbose",
                      default=False, action="store_true",help="verbose output")
    parser.add_option("-p","--pretend", dest="pretend",
                      default=False, action="store_true",help="pretend to do it")
    parser.add_option("-f","--force", dest="force",
                      default=False, action="store_true",help="force mode")

    (options,args) = parser.parse_args()

    if len(args)==0:
        print 'provide at least one directory in argument. Use -h to display help'
        exit(0)
    else:
        dirs = sys.argv[1:]
        for sdir in dirs:
            if not os.path.isdir(sdir):
                continue
            cleanUpDir(sdir, options)
