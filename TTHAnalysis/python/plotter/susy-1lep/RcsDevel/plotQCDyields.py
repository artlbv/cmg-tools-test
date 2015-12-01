import sys,os

from makeYieldPlots import *

_batchMode = False

if __name__ == "__main__":

    CMS_lumi.lumi_13TeV = str(2.1) + " fb^{-1}"
    CMS_lumi.extraText = "Simulation"

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
    mask = basename.replace("*","X_")

        ## Create Yield Storage
    ydsEle = YieldStore("Ele")
    ydsEle.addFromFiles(pattern,("ele","sele"))

    ydsMu = YieldStore("Mu")
    ydsMu.addFromFiles(pattern,("mu","sele"))

    ydsMuAnti = YieldStore("MuAnti")
    ydsMuAnti.addFromFiles(pattern,("mu","anti"))

    # Category
    #cats = ["CR_MB","CR_SB"]
    cats = ["CR_SB"]

    for cat in cats:

        # ele
        colorDict["QCD_Ele_"+cat] = kRed
        hEle = makeSampHisto(ydsEle,"QCD",cat,"QCD_Ele_"+cat)
        hEle.SetTitle("QCD (ele)")

        # muons
        colorDict["QCD_Mu_"+cat] = kBlue
        hMu = makeSampHisto(ydsMu,"QCD",cat,"QCD_Mu_"+cat)
        hMu.SetTitle("QCD (#mu)")

        # muons
        colorDict["QCD_AntiMu_"+cat] = kCyan
        hMuAnti = makeSampHisto(ydsMuAnti,"QCD",cat,"QCD_AntiMu_"+cat)
        hMuAnti.SetTitle("QCD (anti-#mu) x0.1")
        hMuAnti.Scale(1/10.)

        ## MC
        colorDict["MC_Ele_"+cat] = kOrange-3
        hMCele = makeSampHisto(ydsEle,"background",cat,"MC_Ele_"+cat)
        hMCele.SetTitle("MC (ele)")

        colorDict["MC_Mu_"+cat] = kCyan
        hMCmu = makeSampHisto(ydsMu,"background_poisson",cat,"MC_Mu_"+cat)
        hMCmu.SetTitle("MC (#mu)")

        #ratio = getRatio(hMu,hEle)
        #ratio = getPull(hSele,hEle)
        #ratio = getRatio(hEle,hMCele)
        ratio = getRatio(hMu,hMCmu)
        #ratio = getRatio(hMu,hMuAnti)
        #ratio.GetYaxis().SetRangeUser(-0.45,0.45)
        ratio.GetYaxis().SetRangeUser(0,0.105)
        #ratio.GetYaxis().SetRangeUser(0,1.5)

        #canv = plotHists("Sele_Vs_HE_New_EleMu_"+cat,[hEle,hSele],ratio)
        #canv = plotHists("Sele_Vs_New_EleMu_"+cat,[hEle,hSele],ratio)
        #canv = plotHists("Sele_QCDvsMC_Mu_"+cat,[hMCSele,hSele],ratio)
        #canv = plotHists("Sele_QCD_EleVsMu_"+cat,[hEle,hMu],ratio)

        #canv = plotHists("Sele_QCDvsMC_Ele_"+cat,[hMCele,hEle],ratio)
        canv = plotHists("Sele_QCD_vs_MCpois_Mu_"+cat,[hMCmu,hMu],ratio)
        #canv = plotHists("QCD_Mu_Sele_vs_Anti"+cat,[hMuAnti,hMu],ratio)
        #canv = plotHists("Sele_QCDvsMC_Lep_"+cat,[hMCele,hMCmu,hEle,hMu])

        if not _batchMode: raw_input("Enter any key to exit")

        exts = [".pdf",".png"]
        #exts = [".pdf"]
        for ext in exts:
            canv.SaveAs("BinPlots/QCD/lumi2p1/MCCompare/"+mask+canv.GetName()+ext)

