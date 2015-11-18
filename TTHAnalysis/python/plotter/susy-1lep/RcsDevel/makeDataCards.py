#!/usr/bin/env python
import sys

from yieldClass import *
from ROOT import *
def printDataCard(yds, ydsObs, ydsSysSig):
    bins = sorted(yds.keys())
    sampNames = [x.name for x in yds[bins[0]]]
    nSamps = len(sampNames)
    for x in sampNames:
        if "Scan_m" in x: signalName = x
    print signalName
    precision = 4
    
    try:                                                                                                                     
        os.stat('datacards/' + signalName )                                                                                
    except:                                                                                                                  
        os.mkdir('datacards/' + signalName )
    iproc = { key: i for (i,key) in enumerate(reversed(sampNames))}

    for i,bin in enumerate(bins):
        datacard = open('datacards/'+ signalName + '/' +bin + '.card.txt', 'w'); 
        datacard.write("## Datacard for binfile %s (signal %s)\n"%(bin,signalName))
        
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
        datacard.write('bin'+ ( ' ' * 32) +(" ".join([kpatt % bin     for p in sampNames]))+"\n")
        datacard.write('process'+ ( ' ' * 30)  +(" ".join([kpatt % p          for p in sampNames]))+"\n")
        datacard.write('process'+ ( ' ' * 30)  +(" ".join([kpatt % iproc[p]    for p in sampNames]))+"\n")
        datacard.write('rate'+ ( ' ' * 35)  +(" ".join([fpatt % yd.val for yd in yds[bin]]))+"\n")
        #            datacard.write('##----------------------------------\n')
#        datacard.write('Lumi lnN' + (' ' * 33) +  " ".join([kpatt % numToBar(1.0+0.05) for yd in yds[bin]]) + '\n')
        '''for i,yd in enumerate(yds[bin]):
            before = '       -  ' * i
            after = '       -  ' * (nSamps - i - 1)
            datacard.write('MCstats' + yd.name + ' lnN  ' + (' ' * (28-len(yd.name)))  + before + " ".join([kpatt % numToBar(1.0+(yd.err/(yd.val+0.01))) ]) +  after +"\n")        
        '''
        for i, yd in enumerate(ydsSigSys[bin]):
            before = '       -  ' * (nSamps - i - 1)
            sys = yd.name[yd.name.find('Scan_') + 5:yd.name.find('_mGo')]
            datacard.write(sys + ' lnN  ' + (' ' * (28))  + before + " ".join([kpatt % numToBar(1 + yd.val) ]) +"\n")
    return 1



def printABCDCard(yds, ydsObs, ydsKappa, ydsSigSys):
    bins = sorted(yds.keys())
    print [x for x in yds[bins[0]]]
    catNames = [x.cat for x in yds[bins[0]] ]
    sampNames = [x.name for x in (yds[bins[0]]) ]
    sampUniqueNames = list(set(sampNames))
    for x in sampNames:
        if "Scan_m" in x: signalName = x

    catUniqueNames = [x.cat for x in ydsObs[bins[0]] ]
    nSamps = len(sampNames)
    print catNames
    print catUniqueNames
    precision = 4
    
    
    try:                                                                                                                     
        os.stat('datacardsABCD/' + signalName )                                                                                
    except:                                                                                                                  
        os.mkdir('datacardsABCD/' + signalName ) 

    iproc = { key: i for (i,key) in enumerate(sampUniqueNames)}
    for i,bin in enumerate(bins):
        datacard = open('datacardsABCD/'+ signalName+ '/' +bin + '.card.txt', 'w'); 
        datacard.write("## Datacard for bin %s (signal %s)\n"%(bin,signalName))
        datacard.write("imax 4  number of channels \n")
        datacard.write("jmax 1  number of processes -1 \n")
        datacard.write("kmax *  number of nuisance parameters (sources of systematical uncertainties) \n")
        
        klen = len(sampNames)
        kpatt = " %%%ds "  % klen
        fpatt = " %%%d.%df " % (klen,3)
        datacard.write('##----------------------------------\n')
        #observation

        datacard.write('bin'+ ( ' ' * 32) +(" ".join([kpatt % (cat)     for cat in catUniqueNames]))+"\n")
        datacard.write('observation'+ ( ' ' * 32) +(" ".join([fpatt % yd.val  for yd in ydsObs[bin]]))+"\n")
        datacard.write('##----------------------------------\n')
        datacard.write('##----------------------------------\n')
        datacard.write('bin'+ ( ' ' * 32) +(" ".join(([kpatt % (cat)     for cat in catNames])))+"\n")
        datacard.write('process'+ ( ' ' * 30)  +(" ".join([kpatt % p          for p in sampNames]))+"\n")
        datacard.write('process'+ ( ' ' * 30)  +(" ".join([kpatt % iproc[p]    for p in sampNames]))+"\n")

        datacard.write('rate'+ ( ' ' * 37)  +(" ".join([fpatt % yd.val if type(yd) != int and 'Scan' in yd.name else '    1     '  for yd in yds[bin]]))+"\n")
        #            datacard.write('##----------------------------------\n')
#        datacard.write('Lumi lnN' + (' ' * 33) +  " ".join([kpatt % numToBar(1.0+0.05) for yd in yds[bin]]) + '\n')

        before = '       -  ' * (4)
        sys = 'test'
        datacard.write(sys + ' lnN  ' + (' ' * (28))  + before + " ".join([kpatt % numToBar(1 + yd.val) for yd in ydsSigSys[bin]]) +"\n")

        params = ('alpha','beta','gamma','delta')
        for yd,p in zip(ydsObs[bin], params):
            postFix = bin + '_' + yd.cat
            if p == 'alpha':
                datacard.write(p + '_' + bin + ' rateParam ' +yd.cat + ' ' + yd.name + ' (@0*@1/@2*@3) beta_' + bin + ',gamma_' + bin + ',delta_' + bin + ',kappa_' + bin + '\n')
            else:
                datacard.write(p + '_' + bin + ' rateParam ' +yd.cat + ' ' + yd.name + ' ' + numToBar(yd.val) + ' \n')
        kappaVal = ydsKappa[bin][0].val
        kappaErr = ydsKappa[bin][0].err
        datacard.write('kappa_'+ bin + ' param ' + numToBar(kappaVal) +' ' + numToBar(kappaErr) + '\n')
    return 1 

def numToBar(num):
    r = num
    if type(num) == float and abs(num - 1.0) < 0.001:
        r = '   -  '
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
    pattern = "Yields/MC/lumi3fb/full/*/merged/LT*NJ6*"
    yds6.addFromFiles(pattern,("lep","sele")) 
    pattern = "Yields/MC/lumi3fb/full/*/merged/LT*NJ9*"
    yds9.addFromFiles(pattern,("lep","sele"))
    


    #pattern = 'arturstuff/grid/merged/LT\*NJ6\*'

    if 1==1:
        for ydIn in (yds6, yds9):
            cat = 'SR_MB'
            sampsObs = [('background',cat),]
            ydsObs = ydIn.getMixDict(sampsObs)
            sampsBkg = [('TTsemiLep',cat),('TTdiLep',cat),('TTV',cat), ('SingleT',cat), ('WJets',cat), ('DY',cat), ('QCD',cat),]
            sampsSig = [('T1tttt_Scan_mGo1500_mLSP200',cat),]
            sampsSys = [('T1tttt_Scan_Xsec_syst_mGo1500_mLSP200',cat), ]
    #signal still is scaled wrong double check
            samps = sampsBkg + sampsSig
            ydsSig = ydIn.getMixDict(sampsSig)
            yds = ydIn.getMixDict(samps)
            ydsSigSys = ydIn.getMixDict(sampsSys)
            
            printDataCard(yds, ydsObs, ydsSigSys)

            cats = ('SR_MB', 'CR_MB', 'SR_SB','CR_SB')
            sampsABCDbkg = [('background',cat) for cat in cats]
            sampsABCDsig = [('T1tttt_Scan_mGo1500_mLSP200',cat) for cat in cats]
            sampsABCDSigSys = [('T1tttt_Scan_Xsec_syst_mGo1500_mLSP200',cat) for cat in cats ]
            sampsABCD = sampsABCDbkg + sampsABCDsig
            
            ydsABCD = ydIn.getMixDict(sampsABCD)
            ydsObsABCD = ydIn.getMixDict(sampsABCDbkg)
            ydsKappa = ydIn.getMixDict([('EWK','Kappa'), ])
            ydsABCDSigSys = ydIn.getMixDict(sampsABCDSigSys)
            print ydsABCDSigSys
            printABCDCard(ydsABCD, ydsObsABCD, ydsKappa, ydsABCDSigSys)
