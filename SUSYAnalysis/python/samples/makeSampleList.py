#!/usr/bin/env python

listfile = "das_T1tttt_list.txt"

oldPath = "_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15FSPremix-MCRUN2_74_V9-v1/MINIAODSIM"
newPath = "_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15FSPremix-MCRUN2_74_V9-v1/MINIAODSIM"

compLine = "%s = kreator.makeMCComponent(\"%s\",\"%s\",\"CMS\",\".*root\")"

samps = []

with open(listfile,"r") as flist:

    lines = [line for line in flist.readlines() if "#" not in line]

    for line in lines:
        #print line
        line = line.replace("\n","")

        samp = line.replace(oldPath,"")
        samp = samp.replace("/SMS-","")
        samp = samp.replace("-","_")
        samp = samp.replace("Gluino","Go")

        samps.append(samp)
        #print samp
        #print compLine %(samp,samp,line)

print samps
