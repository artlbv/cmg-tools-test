#!/usr/bin/python

import sys,os
import json

def readJSON(fname):
    with open(fname,"r") as fjson:
        jcert = json.load(fjson,parse_int=int)

    cert = {int(k):v for k,v in jcert.iteritems()}

    print "Runs found in JSON", fname
    print cert.keys()

    return cert

def readList(fname):
    evList = set()

    with open(fname,"r") as flist:

        for line in flist.readlines():
            if ":" not in line: continue
            sline = line.split(":")
            if len(sline) != 3: continue
            evList.add((int(sline[0]),int(sline[1]),int(sline[2])))

    return evList

def checkRunLSinList(run,ls,certList):

    if run in certList:
        for lsint in certList[run]:
            if lsint[0] <= ls and ls <= lsint[1]:
                return True
    return False


def skimSet(evList,certList):
    newList = set()

    for (run,ls,evt) in evList:
        if not checkRunLSinList(run,ls,certList):
            newList.add((run,ls,evt))
    return newList

def writeSet(evList,fname = "skimEventList.txt"):

    with open(fname,"w") as f:
        for (run,ls,ev) in sorted(evList):
            line = "%i:%i:%i\n" %(run,ls,ev)
            f.write(line)

if __name__ == "__main__":

    if len(sys.argv) > 2:
        fjsonName = sys.argv[1]
        flistName = sys.argv[2]

        print 'JSON is', fjsonName
        print 'List is', flistName
    else:
        print "Usage:"
        print "skimEventList.py JSONfile List.txt [outname]"

    if len(sys.argv) > 3:
        outname = sys.argv[3]
    else:
        outname = flistName.replace(".txt","") + "_skim_" + fjsonName.replace(".json",".txt")

    print "Outname is:", outname

    #tfile  = TFile(infile, "READ")

    certList = readJSON(fjsonName)
    evList = readList(flistName)

    newEvList = skimSet(evList,certList)

    print "Number of events in:"
    print "Old: %i \t new: %i" %(len(evList),len(newEvList))

    writeSet(newEvList,outname)
