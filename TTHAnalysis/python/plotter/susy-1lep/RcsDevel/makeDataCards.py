#!/usr/bin/env python
import sys

from yieldClass import *
from ROOT import *
def printDataCard(ydsBkg, ydsObs, sampsSig):
    signalPoint =  {'m1': ('mGlu',1500) , 'm2': ('mLSP',100) }
    signalName = ('%s_%s') % signalPoint['m1'] + ('_%s_%s') % signalPoint['m2']
    print ydsBkg
    bins = sorted(ydsBkg.keys())
    sampNames = [x.name for x in ydsBkg[bins[0]]]
    sampNames.append(signalName)
    print sampNames
    precision = 4

    iproc = { key: i for (i,key) in enumerate(reversed(sampNames))}
    for i,bin in enumerate(bins):
        datacard = open('datacards/'+bin + '.card.txt', 'w'); 
        datacard.write("## Datacard for cut file %s (signal %s)\n"%(bin,signalName))
        
            #datacard.write("shapes *        * ../common/%s.input.root x_$PROCESS x_$PROCESS_$SYSTEMATIC\n" % binName)
        datacard.write('##----------------------------------\n')
        datacard.write('bin         %s\n' % bin)
        obs = sum(yd.val for yd in ydsObs[bin])
        datacard.write('observation %s\n' % obs)
        datacard.write('##----------------------------------\n')
        klen = len(sampNames)
        kpatt = " %%%ds "  % klen
        fpatt = " %%%d.%df " % (klen,3)
        datacard.write('##----------------------------------\n')
        datacard.write('bin             '+(" ".join([kpatt % bin     for p in sampNames]))+"\n")
        datacard.write('process         '+(" ".join([kpatt % p          for p in sampNames]))+"\n")
        datacard.write('process         '+(" ".join([kpatt % iproc[p]    for p in sampNames]))+"\n")
        datacard.write('rate            '+(" ".join([fpatt % yd.val for yd in ydsBkg[bin]]))+"\n")
        #            datacard.write('##----------------------------------\n')
        for yd in ydsBkg[bin]:
            datacard.write(('MCstats lnN' ) + " ".join([kpatt % numToBar(1.0+(yd.err/(yd.val+0.01))) +"\n"]))        
    return 1

def numToBar(num):
    r = num
    if type(num) == float and abs(num - 1.0) < 0.001:
        r = '-'
    else: r = '%1.3f' % num
    return r

if __name__ == "__main__":

    ## remove '-b' option
    if '-b' in sys.argv:
        sys.argv.remove('-b')
        _batchMode = True

    if len(sys.argv) > 1:
        pattern = sys.argv[1]
        print '# pattern is', pattern
    else:
        print "No pattern given!"
        exit(0)

    ## Create Yield Storage

    yds6 = YieldStore("lepYields")
    yds9 = YieldStore("lepYields")

    pattern = "lumi3fb_puWeight/grid/merged/LT*NJ6*"
    yds6.addFromFiles(pattern,("lep","sele")) 
    pattern = "lumi3fb_puWeight/grid/merged/LT*NJ9*"
    yds9.addFromFiles(pattern,("lep","sele"))
    


    #pattern = 'arturstuff/grid/merged/LT\*NJ6\*'

    printSamps = ['TTsemiLep','TTdiLep','TTV','SingleT', 'WJets', 'DY', 'QCD','background']

    cat = 'SR_MB'
    sampsBkg = [('TTsemiLep',cat),('TTdiLep',cat),('TTV',cat), ('SingleT',cat), ('WJets',cat), ('DY',cat), ('QCD',cat),]
    ydsBkg = yds6.getMixDict(sampsBkg)
    sampsObs = [('background',cat),]
    ydsObs = yds6.getMixDict(sampsObs)
    yds6.showStats()
    sampsSig = [('TTsemiLep',cat),]
    print 'Obs', ydsObs
    print 'all', yds6
    printDataCard(ydsBkg, ydsObs, sampsSig)
