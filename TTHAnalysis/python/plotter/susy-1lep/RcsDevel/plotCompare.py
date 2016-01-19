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
    pattern = ""

    #BinMask LTX_HTX_NBX_NJX for canvas names
    basename = os.path.basename(pattern)
    mask = basename.replace("*","X_")

    # Define storage
    yds1A = yp.YieldStore("Method1A")
    #btagPath1A = "Yields/btag/test/meth1a/merged"
    #btagPath1A = "Yields/MC/lumi2p24fb/allSF_noPU/btagSF_meth1a/merged"
    #btagPath1A = "Yields/MC/lumi2p24fb_newMC/allSF_noPU/btagSF_meth1a/merged"
    btagPath1A = "Yields/systs/btag/hadFlavour/fixXsec/allSF_noPU/meth1A/merged/"
    yds1A.addFromFiles(btagPath1A,("lep","sele"))

    yds1B = yp.YieldStore("Method1B")
    #btagPath1B = "Yields/btag/test/meth1b/merged"
    #btagPath1B = "Yields/MC/lumi2p24fb/allSF/btagSF_meth1B/merged"
    #btagPath1B = "Yields/btag/test/meth1b/merged"
    #btagPath1B = "Yields/MC/lumi2p24fb/allSF_noPU/btagSF_meth1B/merged"
    #btagPath1B = "Yields/MC/lumi2p24fb/allSF_cutPU/btagSF_meth1a/merged"
    #btagPath1B = "Yields/MC/lumi2p24fb_newMC/allSF_noPU/btagSF_meth1a/merged"
    #btagPath1B = "Yields/MC/lumi2p24fb_newMC/allSF_noPU/btagSF_meth1B/merged"
    btagPath1B = "Yields/systs/btag/hadFlavour/fixXsec/allSF_noPU/meth1B/merged/"
    yds1B.addFromFiles(btagPath1B,("lep","sele"))

    sysCols = [2,4,7,8,3,9,6] + range(10,50)#[1,2,3] + range(4,10)

    # canvs and hists
    hists = []
    canvs = []

    yds1A.showStats()
    yds1B.showStats()

    # Samples
    #samps = ["EWK","TT","TTdiLep","TTsemiLep","WJets","TTV","DY","SingleT"]
    #samps = ["TTJets","WJets","TTV","DY","SingleTop"]
    samps = ["EWK","TTJets","WJets","SingleTop","DY","TTV"]
    samps = ["EWK"]

    cat = "Kappa"
    #cat = "CR_MB"

    #logY = True
    logY = False

    for samp in samps:

        print "Making plot for", samp, cat

        # 1A
        yp.colorDict[samp+"_1A_"+cat] = yp.kBlue
        h1A = yp.makeSampHisto(yds1A,samp,cat,samp+"_1A_"+cat)
        h1A.SetTitle(samp+" (Method 1A)")
        #h1A.SetTitle(samp+" (1A mcFlav)")
        #h1A.SetTitle(samp+" (All SF w/o PU)")

        # 1B
        yp.colorDict[samp+"_1B_"+cat] = yp.kRed
        h1B = yp.makeSampHisto(yds1B,samp,cat,samp+"_1B_"+cat)
        h1B.SetTitle(samp+" (Method 1B)")
        #h1B.SetTitle(samp+" (only btagSF 1B)")
        #h1B.SetTitle(samp+" (All but PU)")
        #h1B.SetTitle(samp+" (PUwgt < 4.)")
        #h1B.SetTitle(samp+" (1A hadrFlav)")

        ratio = yp.getRatio(h1A,h1B)
        #ratio.GetYaxis().SetRangeUser(0.75,1.25)

        #h1A.GetYaxis().SetRangeUser(0.55,1.45)
        if "WJets" in samp and "Kappa" in cat:
            h1B.GetYaxis().SetRangeUser(0.05,3.45)
            h1A.GetYaxis().SetRangeUser(0.05,3.45)

        hists += [h1A,h1B,ratio]
        canv = yp.plotHists(cat+"_"+samp,[h1A,h1B],ratio,"TM", 1200, 600, logY = logY)

        canvs.append(canv)

        if not yp._batchMode:
            answ = raw_input("Enter 'q' to exit: ")
            if "q" in answ: exit(0)

    # Save canvases
    exts = [".pdf",".png"]#,".root"]
    #exts = [".pdf"]

    odir = "BinPlots/btag/Compare/hFlav/1Avs1B/allSF_noPU2/" + cat + "/"
    if not os.path.isdir(odir): os.makedirs(odir)

    for canv in canvs:
        for ext in exts:
            cname = odir+mask+canv.GetName()
            if logY: cname += "_log"
            canv.SaveAs(cname+ext)

