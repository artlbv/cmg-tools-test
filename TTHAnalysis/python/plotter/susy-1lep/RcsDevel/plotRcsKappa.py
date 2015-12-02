import sys,os

#from makeYieldPlots import *
import makeYieldPlots as yp

yp._batchMode = False

if __name__ == "__main__":

    yp.CMS_lumi.lumi_13TeV = str(2.1) + " fb^{-1}"
    yp.CMS_lumi.extraText = "Simulation"

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

    yds = yp.YieldStore("Sele")
    yds.addFromFiles(pattern,("lep","sele"))

    canvs = []

    # Samples
    samps = ["EWK","TT","TTdiLep","TTsemiLep","WJets"]

    for samp in samps:

        # RCS MB
        yp.colorDict[samp+"_Rcs_MB"] = yp.kBlue
        hRcsMB = yp.makeSampHisto(yds,samp,"Rcs_MB",samp+"_Rcs_MB")
        hRcsMB.SetTitle("R_{CS} (MB)")

        # RCS SB
        yp.colorDict[samp+"_Rcs_SB"] = yp.kRed
        hRcsSB = yp.makeSampHisto(yds,samp,"Rcs_SB",samp+"_Rcs_SB")
        hRcsSB.SetTitle("R_{CS} (SB)")

        # Kappa
        yp.colorDict[samp+"_Kappa"] = yp.kBlack
        hKappa = yp.makeSampHisto(yds,samp,"Kappa",samp+"_Kappa")
        hKappa.SetTitle("#kappa")

        yp.prepKappaHist(hKappa)
        yp.prepRatio(hKappa)

        canv = yp.plotHists(samp+"_RcsKappa_",[hRcsMB,hRcsSB],hKappa)
        canvs.append(canv)

        if not yp._batchMode: raw_input("Enter any key to exit")


    # Save canvases
    exts = [".pdf",".png"]
    #exts = [".pdf"]

    odir = "BinPlots/Rcs/test/"

    for canv in canvs:
        for ext in exts:
            canv.SaveAs(odir+mask+canv.GetName()+ext)

