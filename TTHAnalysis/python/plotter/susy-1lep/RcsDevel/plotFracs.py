import sys,os

import  makeYieldPlots as yp

yp._batchMode = False

if __name__ == "__main__":

    yp.CMS_lumi.lumi_13TeV = "MC"
    yp.CMS_lumi.extraText = "Simulation"
    yp.iPos = 0
    if( yp.iPos==0 ): yp.CMS_lumi.relPosX = 0.1


    ## remove '-b' option
    if '-b' in sys.argv:
        sys.argv.remove('-b')
        yp._batchMode = True

    yp._batchMode = False

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
    #mcSamps = ['DY','TTV','SingleT','WJets','TTdiLep','TTsemiLep']
    mcSamps = ['TTdiLep','TTsemiLep','WJets','TTV','SingleT','DY']

    # Category
    #cat = "CR_MB"
    cats = ["CR_SB","SR_SB","CR_MB","SR_MB"]

    for cat in cats:
        # MC samps
        samps = [(samp,cat) for samp in mcSamps]

        hists = yp.makeSampHists(yds,samps)
        total = yp.getTotal(hists)

        for hist in hists:
            hist.Divide(total)
            hist.GetYaxis().SetTitle("Fraction")
        stack = yp.getStack(hists)

        canv = yp.plotHists(cat,[stack],None,"Long")

        if yp._batchMode:
            if "q" in raw_input("Enter any key to exit (or 'q' to stop): "): exit(0)

        exts = [".pdf",".png"]

        odir = "BinPlots/MC/Fractions/"+mask+"/"
        if not os.path.exists(odir): os.makedirs(odir)

        for ext in exts:
            canv.SaveAs(odir+canv.GetName()+ext)
