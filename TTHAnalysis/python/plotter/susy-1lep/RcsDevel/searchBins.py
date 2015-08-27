# LT bins
binsLT = {}
binsLT['LT1'] = '250 < LT && LT < 350'
binsLT['LT2'] = '350 < LT && LT < 450'
binsLT['LT3'] = '450 < LT && LT < 600'
binsLT['LT4'] = '600 < LT'

# HT bins
binsHT = {}
binsHT['HT0'] = '500 < HT && HT < 750'
binsHT['HT1'] = '750 < HT && HT < 1250'
binsHT['HT2'] = '1250 < HT'
binsHT['HT1p2'] = '750 < HT'
binsHT['HT0p1'] = '500 < HT && HT < 1250'

#NB bins
binsNB = {}
#binsNB['NB0'] = 'nBJet == 0'
binsNB['NB1'] = 'nBJet == 1'
binsNB['NB2'] = 'nBJet == 2'
binsNB['NB3'] = 'nBJet >= 3'
binsNB['NB2p3'] = 'nBJet >= 2'


# old
cutDict = {}
cutDict['HT1'] = ' -R "HT HT500 HT>500"'
cutDict['HT2'] = ' -R "HT HT1000 HT>1000"'
