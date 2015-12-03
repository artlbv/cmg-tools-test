import sys,os

import  makeYieldPlots as yp

yp._batchMode = False

if __name__ == "__main__":

    ## remove '-b' option
    if '-b' in sys.argv:
        sys.argv.remove('-b')
        yp._batchMode = True

    if len(sys.argv) > 1:
        pattern = sys.argv[1]
        print '# pattern is', pattern
    else:
        print "No pattern given!"
        exit(0)

    #BinMask LTX_HTX_NBX_NJX for canvas names
    basename = os.path.basename(pattern)
    mask = basename.replace("*","X_")

    ## Create Yield Storage
    yds = yp.YieldStore("lepYields")
    yds.addFromFiles(pattern,("ele","anti"))
    yds.showStats()

    #mcSamps = ['DY','TTV','SingleT','WJets','TT','QCD']
    mcSamps = ['DY','TTV','SingleT','WJets','TT']
    #mcSamps = ['WJets','TT','QCD']

    # Category
    #cat = "CR_MB"
    cats = ["CR_SB","SR_SB","CR_MB","SR_MB"]

    for cat in cats:
        # MC samps
        samps = [(samp,cat) for samp in mcSamps]

        # Totals
        #tots = [("data",cat)]
        tots = [("background",cat)]

        hists = yp.makeSampHists(yds,samps)
        total = yp.getTotal(hists)

        for hist in hists:
            hist.Divide(total)

        stack = yp.getStack(hists)

        hTot = yp.makeSampHists(yds,tots)[0]

        #ratio = getRatio(hTot,total)
        ratio = yp.getRatio(hists[2],total)
        ratio.GetYaxis().SetRangeUser(0,1.25)

        canv = yp.plotHists("Fracs_"+cat,[stack])

        if not yp._batchMode:
            if "q" in raw_input("Enter any key to exit (or 'q' to stop): "): exit(0)

        exts = [".pdf",".png"]
        for ext in exts:
            canv.SaveAs("BinPlots/MC/Fractions/"+mask+canv.GetName()+ext)
