import sys,os

#from makeYieldPlots import *
import makeYieldPlots as yp

yp._batchMode = False

if __name__ == "__main__":

    #yp.CMS_lumi.lumi_13TeV = str(2.1) + " fb^{-1}"
    yp.CMS_lumi.lumi_13TeV = "MC"
    yp.CMS_lumi.extraText = "Simulation"

    ## remove '-b' option
    if '-b' in sys.argv:
        sys.argv.remove('-b')
        yp._batchMode = True

    '''
    if len(sys.argv) > 1:
        pattern = sys.argv[1]
        print '# pattern is', pattern
    else:
        print "No pattern given!"
        exit(0)
    '''
    pattern = "Syst"

    #BinMask LTX_HTX_NBX_NJX for canvas names
    basename = os.path.basename(pattern)
    mask = basename.replace("*","X_")

    # Define storage
    yds = yp.YieldStore("Sele")
    paths = []

    # Add files
    btagPath = "Yields/systs/btag/test/merged/"; paths.append(btagPath)
    puPath = "Yields/systs/PU/test/merged/"; paths.append(puPath)
    wxsecPath = "Yields/systs/wXsec/test/merged/"; paths.append(wxsecPath)
    tptPath = "Yields/systs/topPt/test/merged"; paths.append(tptPath)
    dlConstPath = "Yields/systs/dilepConst/test/merged"; paths.append(dlConstPath)
    dlSlopePath = "Yields/systs/dilepSlope/test/merged"; paths.append(dlSlopePath)

    #jecPath = "Yields/systs/JEC/EWK/full/merged/"; paths.append(jecPath)

    for path in paths:
        yds.addFromFiles(path,("lep","sele"))

    # Sys types
#    systs = ["btagHF","btagLF","Wxsec","PU","topPt"]#,"JEC"]
    systs = ["btagHF","Wxsec","topPt","PU","DLSlope","DLConst"]#,"JEC"]
#    systs = ["topPt"]#,"JEC"]
    sysCols = [1,2,4,7,8,3,9,6] + range(10,50)#[1,2,3] + range(4,10)

    # Sample and variable
    samp = "EWK"
    var = "Kappa"

    # canvs and hists
    hists = []
    canvs = []

    yds.showStats()

    # read in central value
    hCentral = yp.makeSampHisto(yds,samp,var)
    yp.prepRatio(hCentral)

    for i,syst in enumerate(systs):
        yp.colorDict[syst+"_syst"] = sysCols[i]

        sname = samp+"_"+syst+"_syst"
        print "Making hist for", sname

        hist = yp.makeSampHisto(yds,sname,var,syst+"_syst")
        hist.SetTitle(syst)
        hist.GetYaxis().SetTitle("Syst. Err (%)")

        #yp.prepKappaHist(hist)
        #yp.prepRatio(hist)

        # normalize to central value
        hist.Divide(hCentral)

        hists.append(hist)

    # make stack/total syst hists
    #total = yp.getTotal(hists)
    stack = yp.getStack(hists)
    sqHist = yp.getSquaredSum(hists)

    hCentralUncert = yp.getHistWithError(hCentral, sqHist)
    canv = yp.plotHists(var+"_"+samp+"_Syst",[stack,sqHist],[hCentral,hCentralUncert],"TM", 1200, 600)
#    canv = yp.plotHists(var+"_"+samp+"_Stat",[stack,sqHist],hCentral,"TM", 1200, 600)
    canvs.append(canv)
    if not yp._batchMode: raw_input("Enter any key to exit")

    # Save canvases
    exts = [".pdf",".png",".root"]
    #exts = [".pdf"]

    odir = "BinPlots/Syst/test/"

    for canv in canvs:
        for ext in exts:
            canv.SaveAs(odir+mask+canv.GetName()+ext)

