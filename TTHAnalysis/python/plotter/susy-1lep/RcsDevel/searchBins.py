# LT bins
binsLT = {}
binsLT['LT1'] = '250 < LT && LT < 350'
binsLT['LT2'] = '350 < LT && LT < 450'
binsLT['LT3'] = '450 < LT && LT < 600'
binsLT['LT4'] = '600 < LT'
binsLT['LT3p4'] = '450 < LT'

# HT bins
binsHT = {}
binsHT['HT0'] = '500 < HT && HT < 750'
binsHT['HT1'] = '750 < HT && HT < 1250'
binsHT['HT2'] = '1250 < HT'
binsHT['HT1p2'] = '750 < HT'
binsHT['HT0p1'] = '500 < HT && HT < 1250'

# NB bins
binsNB = {}
binsNB['NBi'] = 'nBJet >= 0'
binsNB['NB0'] = 'nBJet == 0'
binsNB['NB1'] = 'nBJet == 1'
binsNB['NB2'] = 'nBJet == 2'
binsNB['NB3'] = 'nBJet >= 3'
binsNB['NB1i'] = 'nBJet >= 1'
binsNB['NB2p3'] = 'nBJet >= 2'

# NJ Bins
binsNJ = {}
#binsNJ['NJi'] = 'nJet >= 4'
binsNJ['NJ45'] = '4 <= nJet && nJet <= 5'
binsNJ['NJ68'] = '6 <= nJet && nJet <= 8'
binsNJ['NJ9i'] = '9 <= nJet'

## Signal/Control region (wrt dPhi)
binsSR = {}
binsSR['SR'] = 'isSR == 1'
binsCR = {}
binsCR['CR'] = 'isSR == 0'

################
# MAKE CUT LISTS
################

cutDict = {}
cutDictSR = {}
cutDictCR = {}

cutDictNJ45 = {}
cutDictNJ68 = {}
cutDictNJ9i = {}


for nj_bin in ['NJ45','NJ68']:#binsNJ.iteritems():
    nj_cut = binsNJ[nj_bin]

    ltbins = ['LT1','LT2','LT3','LT4']

    for lt_bin in ltbins:#binsLT.iteritems():
        lt_cut = binsLT[lt_bin]

        htbins = []

        if lt_bin in ['LT1']:
            htbins += ['HT0','HT1p2']
        if lt_bin in ['LT1','LT2']:
            htbins += ['HT0']
        if lt_bin in ['LT2']:
            htbins += ['HT1']
        if lt_bin in ['LT2','LT3','LT4']:
            htbins += ['HT2']
        if lt_bin in ['LT3','LT4']:
            htbins += ['HT0p1']

        #for ht_bin,ht_cut in binsHT.iteritems():
        for ht_bin in htbins:
            ht_cut = binsHT[ht_bin]

            nbbins = []

            # Match NB bins
            if lt_bin in ['LT1','LT2','LT3','LT4']:
                nbbins += ['NB1'] # NB1 present in all NJ,LT bins
            if lt_bin in ['LT4']:
                nbbins += ['NB2p3'] # NB2p3 present in all NJ,LT bins

            if lt_bin in ['LT1','LT2','LT3']:
                # Signal region binning
                if nj_bin in ['NJ68']:
                    nbbins += ['NB2','NB3']
                # Side band  binning
                if nj_bin in ['NJ45']:
                    nbbins += ['NB2p3']

            for nb_bin in nbbins:
                nb_cut = binsNB[nb_bin]

                binname = "%s_%s_%s_%s" %(lt_bin,ht_bin,nb_bin,nj_bin)
                cutDict[binname] = [("base",lt_bin,lt_cut),("base",ht_bin,ht_cut),("base",nb_bin,nb_cut),("base",nj_bin,nj_cut)]

                # split to SR/CR
                for sr_bin in ['SR']:
                    sr_cut = binsSR[sr_bin]

                    binname = "%s_%s_%s_%s_%s" %(lt_bin,ht_bin,nb_bin,nj_bin,sr_bin)
                    cutDictSR[binname] = [("base",lt_bin,lt_cut),("base",ht_bin,ht_cut),("base",nb_bin,nb_cut),("base",nj_bin,nj_cut),("base",sr_bin,sr_cut)]

                for cr_bin in ['CR']:
                    cr_cut = binsCR[cr_bin]

                    binname = "%s_%s_%s_%s_%s" %(lt_bin,ht_bin,nb_bin,nj_bin,cr_bin)
                    cutDictCR[binname] = [("base",lt_bin,lt_cut),("base",ht_bin,ht_cut),("base",nb_bin,nb_cut),("base",nj_bin,nj_cut),("base",cr_bin,cr_cut)]


### FIXME
for nj_bin in ['NJ9i']:#binsNJ.iteritems():
    nj_cut = binsNJ[nj_bin]

    ltbins = ['LT1','LT2','LT3p4']

    for lt_bin in ltbins:#binsLT.iteritems():
        lt_cut = binsLT[lt_bin]

        htbins = []


        ### FIXME
        if lt_bin in ['LT1']:
            htbins += ['HT0p1','HT2']
        if lt_bin in ['LT1','LT2']:
            htbins += ['HT0']
        if lt_bin in ['LT2']:
            htbins += ['HT1']
        if lt_bin in ['LT2','LT3','LT4']:
            htbins += ['HT2']
        if lt_bin in ['LT3','LT4']:
            htbins += ['HT0p1']

        #for ht_bin,ht_cut in binsHT.iteritems():
        for ht_bin in htbins:
            ht_cut = binsHT[ht_bin]

            nbbins = []

            # Match NB bins
            if lt_bin in ['LT1','LT2']:
                nbbins += ['NB1','NB2','NB3']

            if lt_bin in ['LT3p4']:
                nbbins += ['NB1i']

            for nb_bin in nbbins:
                nb_cut = binsNB[nb_bin]

                binname = "%s_%s_%s_%s" %(lt_bin,ht_bin,nb_bin,nj_bin)

                cutDictNJ9i[binname] = [("base",lt_bin,lt_cut),("base",ht_bin,ht_cut),("base",nb_bin,nb_cut),("base",nj_bin,nj_cut)]
