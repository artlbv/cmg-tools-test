import sys,os

import makeYieldPlots as yp

yp._batchMode = False
yp._alpha = 0.75

if __name__ == "__main__":

    yp.CMS_lumi.lumi_13TeV = str(2.24) + " fb^{-1}"
    yp.CMS_lumi.extraText = "Preliminary"

    #yp.CMS_lumi.lumi_13TeV = "MC"
    #yp.CMS_lumi.extraText = "Simulation"

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

    # canvs and hists
    systHists = []
    canvs = []

    ###########################
    ## Get Kappa Systematics ##
    ###########################

    # Syst storage
    ydsSyst = yp.YieldStore("Syst")
    paths = []

    # Add Syst files
    tptPath = "Yields/systs/topPt/MC/allSF_noPU/meth1A/merged/"; paths.append(tptPath)
    puPath = "Yields/systs/PU/MC/allSF/meth1A/merged/"; paths.append(puPath)
    wxsecPath = "Yields/systs/wXsec/MC/allSF_noPU/meth1A/merged/"; paths.append(wxsecPath)
    dlConstPath = "Yields/systs/DLConst/merged/"; paths.append(dlConstPath)
    dlSlopePath = "Yields/systs/DLSlope/merged/"; paths.append(dlSlopePath)
    #jerPath = "Yields/systs/JER/merged/"; paths.append(jerPath)
    jerNoPath = "Yields/systs/JER_YesNo/merged/"; paths.append(jerNoPath)
    btagPath = "Yields/systs/btag/hadFlavour/fixXsec/allSF_noPU/meth1B/merged/"; paths.append(btagPath)
    jecPath = "Yields/systs/JEC/MC/allSF_noPU/meth1A/merged/"; paths.append(jecPath)

    for path in paths: ydsSyst.addFromFiles(path+basename,("lep","sele"))

    # Sys types
#    systs = ["btagHF","Wxsec","topPt","PU","DLSlope","DLConst"]#,"JEC"]
#    systs = ["Wxsec","PU","JEC","btagHF","btagLF","topPt"]
    systs = ["Wxsec","PU","JEC","btagHF","btagLF","topPt","DLConst","DLSlope","JER"]

    # Kappa systematics
    samp = "EWK";    var = "Kappa"
    systSamps = [(samp+"_"+syst+"_syst",var) for syst in systs]
    systHists = yp.makeSampHists(ydsSyst,systSamps)
    hKappaSysts = yp.getSquaredSum(systHists)

    print "Created syst hist", hKappaSysts

    # MC systematics
    samp = "EWK";    var = "SR_MB"
    systSamps = [(samp+"_"+syst+"_syst",var) for syst in systs]
    systHists = yp.makeSampHists(ydsSyst,systSamps)
    hMCSysts = yp.getSquaredSum(systHists)


    ###########################
    ## Make Prediction plots ##
    ###########################

    ## Create Yield Storage
    yds = yp.YieldStore("lepYields")
    yds.addFromFiles(pattern,("lep","sele"))
    yds.showStats()

    mcSamps = ['DY','TTV','SingleT','WJets','TT']
    #mcSamps = ['EWK']

    # update colors
    yp.colorDict["MC_prediction"] = yp.kRed
    yp.colorDict["Data_prediction"] = yp.kRed

    # Category
    cat = "SR_MB_predict"

    # MC samps
    samps = [(samp,cat) for samp in mcSamps]
    mcHists = yp.makeSampHists(yds,samps)

    mcStack = yp.getStack(mcHists)
    hTotal = yp.getTotal(mcHists)

    # for MC closure
    mcsamp = "EWK_poisson"
    mcsamp = "background_poisson_QCDsubtr"
    hMCpred = yp.makeSampHisto(yds,mcsamp,cat,"MC_prediction"); hMCpred.SetTitle("MC (Pred)")

    # DATA
    hDataPred = yp.makeSampHisto(yds,"data_QCDsubtr",cat,"Data_prediction"); hDataPred.SetTitle("Data (Pred)")
    hData = yp.makeSampHisto(yds,"data_QCDsubtr","SR_MB","Data"); hData.SetTitle("Data")

    ## Append Systematics to prediction
    print "Appending syst. unc. to prediction and total MC"
    hDataPred = yp.getHistWithError(hDataPred, hKappaSysts, new = False)
    hTotal = yp.getHistWithError(hTotal, hMCSysts, new = False)

    # test MC
    #hDataPred = hMCpred

    # Ratio
    #ratio = yp.getRatio(hTotal,hDataPred)
    ratio = yp.getRatio(hData,hDataPred)

    logY = True
    #logY = False
    canv = yp.plotHists("Data_2p24fb_"+cat+'_'+mask,[mcStack,hTotal,hDataPred,hData],ratio,'TM', 1200, 600, logY = logY)
    #canv = yp.plotHists("MC_2p24fb_"+cat+'_'+mask,[mcStack,hTotal,hDataPred],ratio,'TM', 1200, 600, logY = logY)

    if logY: canv.SetName(canv.GetName() + "_log")
    canvs.append(canv)

    if not yp._batchMode: raw_input("Enter any key to exit")

    # Save canvases
    exts = [".pdf",".png",".root"]
    #exts = [".pdf"]

    odir = "BinPlots/Data/Pred/unbld/allSF_noPU/Method1A/"
    #odir = "BinPlots/Syst/btag/hadronFlavour/allSF_noPU/Method1B/"
    if not os.path.isdir(odir): os.makedirs(odir)

    for canv in canvs:
        for ext in exts:
            canv.SaveAs(odir+mask+canv.GetName()+ext)

