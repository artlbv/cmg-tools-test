
#!/usr/bin/env python
import sys
out = ''
from yieldClass import *
from ROOT import *
def printDataCard(yds, ydsObs, ydsSysSig):
    folder = 'datacards_'+ out +'/'
    if not os.path.exists(folder): os.makedirs(folder) 
    bins = sorted(yds.keys())

    sampNames = [x.name for x in yds[bins[0]]]
    nSamps = len(sampNames)
    for x in sampNames:
        if "Scan_m" in x: signalName = x

    precision = 4
    
    try:                                                                                                                     
        os.stat(folder + signalName )                                                                                
    except:                                                                                                                  
        os.mkdir(folder + signalName )
    iproc = { key: i+1 for (i,key) in enumerate(sorted(reversed(sampNames)))}
    iproc.update({signalName: 0})
    
    for i,bin in enumerate(bins):
        datacard = open(folder + signalName + '/' +bin + '.card.txt', 'w'); 
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
    folder = 'datacardsABCD_' + out + '/'
    if not os.path.exists(folder): os.makedirs(folder) 
    bins = sorted(yds.keys())

    catNames = [x.cat for x in yds[bins[0]] ]
    sampNames = [x.name.replace('background','data') for x in (yds[bins[0]]) ]
    sampUniqueNames = list(set(sampNames))
    for x in sampNames:
        if "Scan_m" in x: signalName = x

    catUniqueNames = [x.cat for x in ydsObs[bins[0]] ]
    nSamps = len(sampNames)

    precision = 4
    
    
    try:                                                                                                                     
        os.stat(folder + signalName )                                                                                
    except:                                                                                                                  
        os.mkdir(folder + signalName ) 

    #print sampUniqueNames
    iproc = { key: i+1 for (i,key) in enumerate(sorted(reversed(sampUniqueNames)))}
    iproc.update({signalName: 0})
    #print iproc
    for i,bin in enumerate(bins):
        datacard = open(folder+ signalName+ '/' +bin + '.card.txt', 'w'); 
        datacard.write("## Datacard for bin %s (signal %s)\n"%(bin,signalName))
        datacard.write("imax 4  number of channels \n")
        datacard.write("jmax 1  number of processes -1 \n")
        datacard.write("kmax *  number of nuisance parameters (sources of systematical uncertainties) \n")
        
        klen = len(sampNames)
        kpatt = " %%%ds "  % klen
        fpatt = " %%%d.%df " % (klen,3)
        datacard.write('##----------------------------------\n')
        #observation

        datacard.write('bin'+ ( ' ' * 32) +(" ".join([kpatt % cat.replace('_predict','')     for cat in catUniqueNames]))+"\n")
        datacard.write('observation'+ ( ' ' * 32) +(" ".join([kpatt % round(yd.val)  for yd in ydsObs[bin]]))+"\n")
        datacard.write('##----------------------------------\n')
        datacard.write('##----------------------------------\n')
        datacard.write('bin'+ ( ' ' * 32) +(" ".join(([kpatt % (cat.replace('_predict',''))     for cat in catNames])))+"\n")
        datacard.write('process'+ ( ' ' * 30)  +(" ".join([kpatt % p          for p in sampNames]))+"\n")
        datacard.write('process'+ ( ' ' * 30)  +(" ".join([kpatt % iproc[p]    for p in sampNames]))+"\n")

        datacard.write('rate'+ ( ' ' * 37)  +(" ".join([fpatt % yd.val if type(yd) != int and 'Scan' in yd.name else '   1     '  for yd in yds[bin]]))+"\n")
        #            datacard.write('##----------------------------------\n')
#        datacard.write('Lumi lnN' + (' ' * 33) +  " ".join([kpatt % numToBar(1.0+0.05) for yd in yds[bin]]) + '\n')

        before = '       -  ' * (4)
        sys = 'test'
        datacard.write(sys + ' lnN  ' + (' ' * (28))  + before + " ".join([kpatt % numToBar(1 + yd.val) for yd in ydsSigSys[bin]]) +"\n")

    
        params = ('kappa','beta','delta')
        addParam = ''
        betaQCDname= ''
        deltaQCDname= ''
        for yd,p in zip(ydsKappa[bin], params):
            Val = yd.val
            Err = yd.err
            Name = yd.name
            SB = yd.sbname
            MB = yd.mbname
            Label = yd.label

            if 'QCD' in yd.name: name = p+yd.name +'_'+ Label 
            if Val > 0.01 and p == 'beta':
                addParam = addParam+p
                betaQCDname = Name+'_'+Label
                datacard.write(name + ' param ' + numToBar(Val) +' ' + numToBar(Err) + '\n')
            elif Val > 0.01 and p == 'delta':
                addParam = addParam + p
                deltaQCDname = Name+'_'+Label
                datacard.write(name + ' param ' + numToBar(Val) +' ' + numToBar(Err) + '\n')
            elif p == 'kappa':
                name = p+'_'+ bin
                datacard.write(name + ' param ' + numToBar(Val) +' ' + numToBar(Err) + '\n')

        betaName = ''; gammaName = ''; deltaName = '';
        params = ('alpha','beta','gamma','delta')
        for yd,p in zip(ydsObs[bin], params):
            if p == 'beta': betaName = yd.label
            if p == 'gamma': gammaName = yd.label
            if p == 'delta': deltaName = yd.label



        formula = '(@0*@1/@2*@3)'
        paramIn = 'beta_' + betaName + ',gamma_' + gammaName + ',delta_' + deltaName + ',kappa_' + bin
        if 'beta' in addParam and 'delta' in addParam: 
            formula = formula.replace('@0','(@0-@4)').replace('@2','(@2-@5)')
            paramIn = paramIn +',beta' + betaQCDname + ',delta' + deltaQCDname
        elif addParam == 'beta':
            formula = formula.replace('@0','(@0-@4)')
            paramIn = paramIn +',beta' + betaQCDname
        elif addParam == 'delta': 
            formula = formula.replace('@2','(@2-@4)')
            paramIn = paramIn +',delta' + deltaQCDname

            
        for yd,p in zip(ydsObs[bin], params):
            postFix = bin + '_' + yd.cat
            if p == 'alpha':
                datacard.write(p + '_' + yd.label + ' rateParam ' +yd.cat.replace('_predict','') + ' ' + yd.name.replace('background','data') + ' ' + formula + ' ' + paramIn + '\n')
            else:
                datacard.write(p + '_' + yd.label + ' rateParam ' +yd.cat.replace('_predict','') + ' ' + yd.name.replace('background','data')  + ' ' + str(round(yd.val)) + ' \n')

        
                
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

    if len(sys.argv) > 2:
        pattern = sys.argv[1]
        out = sys.argv[2]
        print '# pattern is', pattern
        print '# out is', out
    else:
        print "No pattern given!"
        exit(0)

    ## Create Yield Storage

    yds6 = YieldStore("lepYields")
    yds9 = YieldStore("lepYields")
    pattern = "Yields/all/lumi2p1fb_MC1_2fbbins_noPU/full/*/merged/LT*NJ6*"
    yds6.addFromFiles(pattern,("lep","sele")) 
    pattern = "Yields/all/lumi2p1fb_MC1_2fbbins_noPU/full/*/merged/LT*NJ9*"
    yds9.addFromFiles(pattern,("lep","sele"))
    

#    yds6.showStats()
#    yds9.showStats()
    #pattern = 'arturstuff/grid/merged/LT\*NJ6\*'

    for mGo in range(800, 1700, 100):
        for mLSP in range(50,1200,50):
#    for mGo in range(1500, 1600, 50):
#        for mLSP in range(100,200,50):
            for ydIn in (yds6, yds9):
                print "making datacards for "+str(mGo)+ ' '+str(mLSP)
                signal = 'T1tttt_Scan_mGo'+str(mGo)+'_mLSP'+str(mLSP)
                cat = 'SR_MB'
                sampsObs = [('background',cat),]
                ydsObs = ydIn.getMixDict(sampsObs)
                sampsBkg = [('TTsemiLep',cat),('TTdiLep',cat),('TTV',cat), ('SingleT',cat), ('WJets',cat), ('DY',cat), ('QCD',cat),]
                sampsSig = [(signal ,cat),]
                sampsSys = [('T1tttt_Scan_Xsec_syst_mGo'+str(mGo)+'_mLSP'+str(mLSP),cat), ]
    #signal still is scaled wrong double check
                samps = sampsBkg + sampsSig
                ydsSig = ydIn.getMixDict(sampsSig)
                if type(ydsSig.values()[0][0]) == int:
                    print "signal not available will skip"
                    continue
                
                yds = ydIn.getMixDict(samps)
                ydsSigSys = ydIn.getMixDict(sampsSys)
                
                printDataCard(yds, ydsObs, ydsSigSys)
                
                cats = ('SR_MB', 'CR_MB', 'SR_SB','CR_SB')
                catsNoSR = ('CR_MB', 'SR_SB','CR_SB')
                
                sampsABCDbkg = [('data',cat) for cat in catsNoSR]
                print sampsABCDbkg
#                sampsABCDbkg.insert(0,('data','SR_MB_predict'))
                sampsABCDbkg.insert(0,('background','SR_MB'))
#                print sampsABCDbkg
                sampsABCDsig = [('T1tttt_Scan_mGo'+str(mGo)+'_mLSP'+str(mLSP),cat) for cat in cats]
                sampsABCDSigSys = [('T1tttt_Scan_Xsec_syst_mGo'+str(mGo)+'_mLSP'+str(mLSP),cat) for cat in cats ]
                sampsABCD = sampsABCDbkg + sampsABCDsig
                
                ydsABCD = ydIn.getMixDict(sampsABCD)
                ydsObsABCD = ydIn.getMixDict(sampsABCDbkg)
                ydsKappa = ydIn.getMixDict([('EWK','Kappa'), ('QCD_QCDpred','CR_MB'), ('QCD_QCDpred','CR_SB') ])
                ydsABCDSigSys = ydIn.getMixDict(sampsABCDSigSys)
                
                printABCDCard(ydsABCD, ydsObsABCD, ydsKappa, ydsABCDSigSys)
                
