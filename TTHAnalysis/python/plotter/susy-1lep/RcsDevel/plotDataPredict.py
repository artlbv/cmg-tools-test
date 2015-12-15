import sys,os

from makeYieldPlots import *

_batchMode = False

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

    #BinMask LTX_HTX_NBX_NJX for canvas names
    basename = os.path.basename(pattern)
    #basename = basename.replace("_SR","")
    mask = basename.replace("*","X_")

    ## Create Yield Storage
    yds = YieldStore("lepYields")
    yds.addFromFiles(pattern,("lep","sele"))
    yds.showStats()

    mcSamps = ['DY','QCD','TTV','SingleT','WJets','TT']#
    #mcSamps = ['WJets','TT','QCD']

    # update colors
    colorDict["MC_prediction"] = kGreen
    colorDict["Data_prediction"] = kRed

    CMS_lumi.lumi_13TeV = str(2.1) + " fb^{-1}"
    CMS_lumi.extraText = "Preliminary"

    # Category
    #cat = "CR_MB"
    cats = ["SR_MB_predict"]

    for cat in cats:
        # MC samps
        samps = [(samp,cat) for samp in mcSamps]

        mcHists = makeSampHists(yds,samps)
        stack = getStack(mcHists)
        total = getTotal(mcHists)

        # Totals
        hMCpred = makeSampHisto(yds,"background_QCDsubtr",cat,"MC_prediction"); hMCpred.SetTitle("MC (Pred)")
        hDataPred = makeSampHisto(yds,"data_QCDsubtr",cat,"Data_prediction"); hDataPred.SetTitle("Data (Pred)")
        hData = makeSampHisto(yds,"data_QCDsubtr","SR_MB","Data"); hData.SetTitle("Data")

        ratio = getRatio(hData,hDataPred)
        #ratio = getPull(hData,hDataPred)
        #ratio.GetYaxis().SetRangeUser(0,5)

        #canv = plotHists("DataNJ45_"+cat,[stack,hMCpred,hDataPred,hData,total],ratio)
        canv = plotHists("DataNJ45_2p1fb_"+cat+'_'+mask,[stack,total,hDataPred,hData],ratio,'TM', 1200, 600)
        print canv.GetName()
        for hist in [stack,total,hDataPred,hData]:
            hist.GetYaxis().SetRangeUser(0,15)

        if not _batchMode:
            if "q" in raw_input("Enter any key to exit (or 'q' to stop): "): exit(0)

        exts = [".pdf",".png",".root"]
        for ext in exts:
            canv.SaveAs("BinPlots/Data/stacks/"+canv.GetName()+ext)

