import sys,os

#from makeYieldPlots import *
import makeYieldPlots as yp

yp._batchMode = False
yp._alpha = 0.8

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

    ## Store dict in pickle file
    storeDict = True

    if storeDict == True and os.path.exists("allSysts.pck"):

        print "#Loading saved yields from pickle!"

        import cPickle as pickle
        yds = pickle.load( open( "allSysts.pck", "rb" ) )
        yds.showStats()

    else:

        print "#Reading yields from files!"

        # Define storage
        yds = yp.YieldStore("Sele")
        paths = []

        # Add files
        tptPath = "Yields/systs/topPt/MC/allSF_noPU/meth1A/merged/"; paths.append(tptPath)
        puPath = "Yields/systs/PU/MC/allSF/meth1A/merged/"; paths.append(puPath)
        wxsecPath = "Yields/systs/wXsec/MC/allSF_noPU/meth1A/merged/"; paths.append(wxsecPath)
        ttvxsecPath = "Yields/systs/TTVxsec/MC/allSF_noPU/meth1A/merged/"; paths.append(ttvxsecPath)
        wpolPath = "Yields/systs/Wpol/MC/allSF_noPU/meth1A/merged/"; paths.append(wpolPath)
        dlConstPath = "Yields/systs/DLConst/merged"; paths.append(dlConstPath)
        dlSlopePath = "Yields/systs/DLSlope/merged"; paths.append(dlSlopePath)
        jerPath = "Yields/systs/JER/merged"; paths.append(jerPath)
        jerNoPath = "Yields/systs/JER_YesNo/merged"; paths.append(jerNoPath)
        btagPath = "Yields/systs/btag/hadFlavour/fixXsec/allSF_noPU/meth1A/merged/"; paths.append(btagPath)
        jecPath = "Yields/systs/JEC/MC/allSF_noPU/meth1A/merged/"; paths.append(jecPath)

        for path in paths:
            yds.addFromFiles(path,("lep","sele"))

        yds.showStats()

        print "#Saving yields to pickle"

        # save to pickle
        import cPickle as pickle
        pickle.dump( yds, open( "allSysts.pck", "wb" ) )

    #print [name for name in yds.samples if ("syst" in name and "EWK" in name)]
    #exit(0)

    # Sys types
#    systs = ["btagHF","btagLF","Wxsec","PU"]#,"topPt"]#,"JEC"]
#    systs = ["btagHF","btagLF","Wxsec","PU","topPt"]#,"JEC"]
#    systs = ["btagHF","Wxsec","topPt","PU","DLSlope","DLConst"]#,"JEC"]
#    systs = ["JEC"]
#    systs = ["btagHF","btagLF"]
#    systs = ["btagLF","btagHF"]
#    systs = ["DLConst","DLSlope"]

#    systs = ["TTVxsec","Wxsec"]
#    systs = ["Wpol","Wxsec"]
#    systs = ["Wpol","Wxsec","PU","JEC","btagHF","btagLF","topPt","DLConst","DLSlope","JER","JERYesNo"]
    systs = ["TTVxsec","Wpol","Wxsec","PU","JEC","btagHF","btagLF","topPt","DLConst","DLSlope"]

    systNames = {
        "btagLF" : "b-mistag (light)",
        "btagHF" : "b-tag (b/c)",
        "JEC" : "JEC",
        "topPt" : "Top p_{T}",
        "PU" : "PU",
        #"Wxsec" : "#sigma_{W}",
        "Wxsec" : "W x-sec",
        "TTVxsec" : "TTV x-sec",
        "Wpol" : "W polar.",
        "JER" : "JER",
        "JERYesNo" : "JER Yes/No",
        "DLSlope" : "DiLep (N_{j} Slope)",
        "DLConst" : "DiLep (N_{j} Const)",
        }

    #sysCols = [2,4,7,8,3,9,6] + range(40,50)#[1,2,3] + range(4,10)
    #sysCols = [50] + range(49,0,-2)#range(30,50,2)
    #sysCols = range(40,100,1)#range(30,50,2)
    #sysCols = range(35,100,3)
    sysCols = range(28,100,2)
    #sysCols = range(49,1,-2)
    #sysCols = range(30,40,4) + range(40,100,3)
    #sysCols = range(49,40,-2) + range(40,30,-3) + range(50,100,5)

    # Sample and variable
    samp = "EWK"
    #samps = ["TTJets","WJets","SingleTop","DY","TTV"]
    #samps = ['T_tWch','TToLeptons_tch','TBar_tWch', 'TToLeptons_sch',"EWK"]
    #samp = samps[4]

    var = "Kappa"
    #var = "SR_SB"

    # canvs and hists
    hists = []
    canvs = []

    # read in central value
    hCentral = yp.makeSampHisto(yds,samp,var)
    yp.prepRatio(hCentral)

    for i,syst in enumerate(systs):
        yp.colorDict[syst+"_syst"] = sysCols[i]

        sname = samp+"_"+syst+"_syst"
        print "Making hist for", sname

        hist = yp.makeSampHisto(yds,sname,var,syst+"_syst")
        if syst in systNames: hist.SetTitle(systNames[syst])
        else: hist.SetTitle(syst)

        hist.GetYaxis().SetTitle("Relative uncertainty")
        hist.GetYaxis().SetTitleSize(0.04)
        hist.GetYaxis().SetTitleOffset(0.8)

        #yp.prepKappaHist(hist)
        #yp.prepRatio(hist)

        # normalize to central value
        #hist.Divide(hCentral)

        hists.append(hist)

    # make stack/total syst hists
    #total = yp.getTotal(hists)
    stack = yp.getStack(hists)
    sqHist = yp.getSquaredSum(hists)

    hCentralUncert = yp.getHistWithError(hCentral, sqHist)
    canv = yp.plotHists(var+"_"+samp+"_Syst",[stack,sqHist],[hCentral,hCentralUncert],"TM", 1200, 600)
#    canv = yp.plotHists(var+"_"+samp+"_Syst",[sqHist]+hists,[hCentral,hCentralUncert],"TM", 1200, 600)
#    canv = yp.plotHists(var+"_"+samp+"_Stat",[stack,sqHist],hCentral,"TM", 1200, 600)

    canvs.append(canv)
    if not yp._batchMode: raw_input("Enter any key to exit")

    # Save canvases
    exts = [".pdf",".png",".root"]
    #exts = [".pdf"]

    #odir = "BinPlots/Syst/Combine/test/allSF_noPU_Wpol/Method1A/"
    odir = "BinPlots/Syst/Combine/allSF_noPU_Wpol/Method1A/"
    if not os.path.isdir(odir): os.makedirs(odir)

    ## Save hists
    pattern = "Syst"
    mask = pattern

    for canv in canvs:
        for ext in exts:
            canv.SaveAs(odir+mask+canv.GetName()+ext)

