'''
Created by Francesco
29 November 2021
'''
#functions and script to compute correlations in space and time
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm
import utilsCorr as ucorr
import utilsPlot as uplot
import sys
import os

########################### Pair Correlation Function ##########################
def computePairCorr(dirName, plot="plot"):
    boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    phi = ucorr.readFromParams(dirName, "phi")
    rad = np.loadtxt(dirName + os.sep + "particleRad.dat")
    meanRad = np.mean(rad)
    bins = np.linspace(0.1*meanRad, 10*meanRad, 50)
    pos = ucorr.getPBCPositions(dirName + os.sep + dir + "/particlePos.dat", boxSize)
    distance = ucorr.computeDistances(pos, boxSize)
    pairCorr, edges = np.histogram(distance, bins=bins, density=True)
    binCenter = 0.5 * (edges[:-1] + edges[1:])
    pairCorr /= (2 * np.pi * binCenter)
    firstPeak = binCenter[np.argmax(pairCorr)]
    print("First peak of pair corr is at distance:", firstPeak, "equal to", firstPeak/meanRad, "times the mean radius:", meanRad)
    if(plot == "plot"):
        uplot.plotCorrelation(binCenter, pairCorr, "$Pair$ $correlation$ $function,$ $g(r)$")
        plt.show()
    else:
        return firstPeak

############################ Particle Susceptibility ###########################
def computeParticleSusceptibility(dirName, sampleName, maxPower):
    numParticles = ucorr.readFromParams(dirName, "numParticles")
    boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    timeStep = ucorr.readFromParams(dirName, "dt")
    particleChi = []
    particleCorr = []
    # get trajectory directories
    stepRange = ucorr.getDirectories(dirName)
    stepRange = np.array(np.char.strip(stepRange, 't'), dtype=int)
    stepRange = np.sort(stepRange)
    pPos0 = np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[0]) + "/particlePos.dat"))
    pos0 = np.array(np.loadtxt(dirName + os.sep + "../" + sampleName + "/t" + str(stepRange[0]) + "/particlePos.dat"))
    pField = np.array(np.loadtxt(dirName + os.sep + "externalField.dat"))
    pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[0]) + "/particleRad.dat")))
    pWaveVector = np.pi / pRad
    damping = 1e03
    scale = pRad**2
    stepRange = stepRange[stepRange<int(10**maxPower)]
    for i in range(1,stepRange.shape[0]):
        pPos = np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[i]) + "/particlePos.dat"))
        pos = np.array(np.loadtxt(dirName + os.sep + "../" + sampleName + "/t" + str(stepRange[i]) + "/particlePos.dat"))
        particleChi.append(ucorr.computeSusceptibility(pPos, pPos0, pField, pWaveVector, scale))
        #particleChi.append(ucorr.computeCorrFunctions(pPos, pPos0, boxSize, pWaveVector, scale, oneDim = True))
        particleCorr.append(ucorr.computeCorrFunctions(pos, pos0, boxSize, pWaveVector, scale, oneDim = True))
    particleChi = np.array(particleChi)
    particleCorr = np.array(particleCorr).reshape((stepRange.shape[0]-1,7))
    stepRange = stepRange[1:]#discard initial time
    np.savetxt(dirName + os.sep + "sus-lin-xdim.dat", np.column_stack((stepRange*timeStep, particleChi)))
    np.savetxt(dirName + os.sep + "../dynamics-test/corr-lin-xdim.dat", np.column_stack((stepRange*timeStep, particleCorr)))
    print("susceptibility: ", np.mean(particleChi[-20:,0]/(stepRange[-20:]*timeStep)), " ", np.std(particleChi[-20:,0]/(stepRange[-20:]*timeStep)))
    #uplot.plotCorrelation(stepRange*timeStep, particleChi[:,0]/(stepRange*timeStep), "$\\chi_0/t$", "$Simulation$ $step$", logx = True, color='k')
    #uplot.plotCorrelation(stepRange*timeStep, particleCorr[:,0]/(2*particleChi[:,0]), "$T_{FDT}$", "$Simulation$ $step$", logx = True, color='k')
    uplot.plotCorrelation(particleCorr[:,1], particleChi[:,1], "$\\chi$", "$ISF$", color='k')

###################### One Dim Particle Self Correlations ######################
def computeParticleSelfCorrOneDim(dirName, maxPower):
    numParticles = ucorr.readFromParams(dirName, "numParticles")
    boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    phi = ucorr.readFromParams(dirName, "phi")
    timeStep = ucorr.readFromParams(dirName, "dt")
    #pWaveVector = np.pi / (2 * np.sqrt(boxSize[0] * boxSize[1] * phi / (np.pi * numParticles)))
    #pWaveVector = np.pi / computePairCorr(dirName, plot=False)
    pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "particleRad.dat")))
    pWaveVector = np.pi / pRad
    print("wave vector: ", pWaveVector)
    particleCorr = []
    # get trajectory directories
    stepRange = ucorr.getDirectories(dirName)
    stepRange = np.array(np.char.strip(stepRange, 't'), dtype=int)
    stepRange = np.sort(stepRange)
    pPos0 = np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[0]) + "/particlePos.dat"))
    pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[0]) + "/particleRad.dat")))
    stepRange = stepRange[stepRange<int(10**maxPower)]
    for i in range(1,stepRange.shape[0]):
        pPos = np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[i]) + "/particlePos.dat"))
        particleCorr.append(ucorr.computeCorrFunctions(pPos, pPos0, boxSize, pWaveVector, pRad**2, oneDim = True))
    particleCorr = np.array(particleCorr).reshape((stepRange.shape[0]-1,7))
    stepRange = stepRange[1:]#discard initial time
    np.savetxt(dirName + os.sep + "corr-lin-xdim.dat", np.column_stack((stepRange * timeStep, particleCorr)))
    print("diffusivity: ", np.mean(particleCorr[-20:,0]/(2*stepRange[-20:]*timeStep)), " ", np.std(particleCorr[-20:,0]/(2*stepRange[-20:]*timeStep)))
    uplot.plotCorrelation(stepRange * timeStep, particleCorr[:,0]/(stepRange*timeStep), "$MSD(t)/t$", "$Simulation$ $time,$ $t$", logx = True, color='k')
    #uplot.plotCorrelation(stepRange * timeStep, particleCorr[:,0], "$MSD(\\Delta t)$", "$time$ $interval,$ $\\Delta t$", logx = True, logy = True, color='k')

########### One Dim Time-averaged Self Corr in log-spaced time window ##########
def computeParticleLogSelfCorrOneDim(dirName, startBlock, maxPower, freqPower):
    numParticles = ucorr.readFromParams(dirName, "numParticles")
    boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "particleRad.dat")))
    phi = ucorr.readFromParams(dirName, "phi")
    timeStep = ucorr.readFromParams(dirName, "dt")
    T = np.mean(np.loadtxt(dirName + "energy.dat")[:,4])
    pWaveVector = np.pi / pRad
    print("wave vector: ", pWaveVector)
    particleCorr = []
    stepList = []
    freqDecade = int(10**freqPower)
    decadeSpacing = 10
    spacingDecade = 1
    stepDecade = 10
    numBlocks = int(10**(maxPower-freqPower))
    for power in range(maxPower):
        for spacing in range(1,decadeSpacing):
            stepRange = np.arange(0,stepDecade,spacing*spacingDecade,dtype=int)
            #print(stepRange, spacing*spacingDecade)
            stepParticleCorr = []
            numPairs = 0
            for multiple in range(startBlock, numBlocks):
                for i in range(stepRange.shape[0]-1):
                    if(ucorr.checkPair(dirName, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])):
                        #print(multiple, i, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])
                        pPos1, pPos2 = ucorr.readParticlePair(dirName, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])
                        stepParticleCorr.append(ucorr.computeCorrFunctions(pPos1, pPos2, boxSize, pWaveVector, pRad**2, oneDim = True))
                        numPairs += 1
            if(numPairs > 0):
                stepList.append(spacing*spacingDecade)
                particleCorr.append(np.mean(stepParticleCorr, axis=0))
        stepDecade *= 10
        spacingDecade *= 10
    stepList = np.array(stepList)
    particleCorr = np.array(particleCorr).reshape((stepList.shape[0],7))
    particleCorr = particleCorr[np.argsort(stepList)]
    np.savetxt(dirName + os.sep + "corr-log-xdim.dat", np.column_stack((stepList * timeStep, particleCorr)))
    print("diffusivity on x: ", np.mean(particleCorr[-20:,0]/(2*stepList[-20:]*timeStep)), " ", np.std(particleCorr[-20:,0]/(2*stepList[-20:]*timeStep)))
    uplot.plotCorrelation(stepList * timeStep, particleCorr[:,0]/(stepList*timeStep), "$MSD(\\Delta t)/\\Delta t$", "$time$ $interval,$ $\\Delta t$", logx = True, color = 'r')
    #uplot.plotCorrelation(stepList * timeStep, particleCorr[:,0], "$MSD(\\Delta t)$", "$time$ $interval,$ $\\Delta t$", logx = True, logy = True, color = 'r')
    #uplot.plotCorrelation(stepList * timeStep, particleCorr[:,1], "$ISF(t)$", "$time$ $interval,$ $\\Delta t$", logx = True, color = 'r')

########################## Particle Self Correlations ##########################
def computeParticleSelfCorr(dirName, maxPower):
    computeFrom = 20
    numParticles = ucorr.readFromParams(dirName, "numParticles")
    boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    phi = ucorr.readFromParams(dirName, "phi")
    timeStep = ucorr.readFromParams(dirName, "dt")
    #pWaveVector = np.pi / (2 * np.sqrt(boxSize[0] * boxSize[1] * phi / (np.pi * numParticles)))
    #pWaveVector = np.pi / computePairCorr(dirName, plot=False)
    pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "particleRad.dat")))
    pWaveVector = np.pi / pRad
    particleCorr = []
    # get trajectory directories
    stepRange = ucorr.getDirectories(dirName)
    stepRange = np.array(np.char.strip(stepRange, 't'), dtype=int)
    stepRange = np.sort(stepRange)
    pPos0 = np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[0]) + "/particlePos.dat"))
    pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[0]) + "/particleRad.dat")))
    stepRange = stepRange[stepRange<int(10**maxPower)]
    for i in range(1,stepRange.shape[0]):
        pPos = np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[i]) + "/particlePos.dat"))
        particleCorr.append(ucorr.computeCorrFunctions(pPos, pPos0, boxSize, pWaveVector, pRad**2))
        #particleCorr.append(ucorr.computeScatteringFunctions(pPos, pPos0, boxSize, pWaveVector, pRad**2))
    particleCorr = np.array(particleCorr).reshape((stepRange.shape[0]-1,7))
    stepRange = stepRange[1:]#discard initial time
    np.savetxt(dirName + os.sep + "corr-lin.dat", np.column_stack((stepRange*timeStep, particleCorr)))
    #print("diffusivity: ", np.mean(particleCorr[-20:,0]/(4*stepRange[-20:]*timeStep)), " ", np.std(particleCorr[-20:,0]/(4*stepRange[-20:]*timeStep)))
    #uplot.plotCorrelation(stepRange * timeStep, particleCorr[:,0], "$MSD(\\Delta t)$", "$time$ $interval,$ $\\Delta t$", logy = True, logx = True, color = 'k')
    uplot.plotCorrelation(stepRange * timeStep, particleCorr[:,1], "$ISF(\\Delta t)$", "$time$ $interval,$ $\\Delta t$", logx = True, color = 'r')

########## Check Self Correlations by logarithmically spaced blocks ############
def checkParticleSelfCorr(dirName, initialBlock, numBlocks, maxPower, plot="plot", computeTau="tau"):
    colorList = cm.get_cmap('viridis', 10)
    numParticles = ucorr.readFromParams(dirName, "numParticles")
    boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    phi = ucorr.readFromParams(dirName, "phi")
    timeStep = ucorr.readFromParams(dirName, "dt")
    energy = np.loadtxt(dirName + "/energy.dat")
    if(energy[-1,3] < energy[-1,4]):
        T = np.mean(energy[:,3])
    else:
        T = np.mean(energy[:,4])
    print(T)
    #pWaveVector = np.pi / (np.sqrt(boxSize[0] * boxSize[1] * phi / (np.pi * numParticles)))
    #pWaveVector = np.pi /computePairCorr(dirName, plot=False)
    #pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "particleRad.dat")))
    firstPeak = np.loadtxt(dirName + os.sep + "pcorrFirstPeak.dat")[0]
    pWaveVector = 2*np.pi / firstPeak
    print("wave vector: ", pWaveVector)
    tau = []
    diff = []
    # get trajectory directories
    stepRange = ucorr.getDirectories(dirName)
    stepRange = np.array(np.char.strip(stepRange, 't'), dtype=int)
    stepRange = np.sort(stepRange)
    decade = int(10**(maxPower-1))
    start = np.argwhere(stepRange==(initialBlock-1)*decade)[0,0]
    for block in np.arange(initialBlock, numBlocks+1, 1, dtype=int):
        particleCorr = []
        pPos0 = np.array(np.loadtxt(dirName + os.sep + "t" + str((block-1)*decade) + "/particlePos.dat"))
        pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "t" + str((block-1)*decade) + "/particleRad.dat")))
        end = np.argwhere(stepRange==(block*decade-int(decade/10)))[0,0]
        #print((block-1)*decade, start, block*decade, end)
        stepBlock = stepRange[start:end+1]
        print(stepBlock[0], stepBlock[-1])
        start = end+1
        for i in range(1,stepBlock.shape[0]):
            pPos = np.array(np.loadtxt(dirName + os.sep + "t" + str(stepBlock[i]) + "/particlePos.dat"))
            particleCorr.append(ucorr.computeCorrFunctions(pPos, pPos0, boxSize, pWaveVector, pRad**2))
        particleCorr = np.array(particleCorr).reshape((stepBlock.shape[0]-1,7))
        stepBlock = stepBlock[1:]-(block-1)*decade#discard initial time
        if(plot=="plot"):
            #uplot.plotCorrelation(stepBlock*timeStep, particleCorr[:,0], "$MSD(\\Delta t)$", "$time$ $interval,$ $\\Delta t$", logx = True, logy = True, color=colorList(block/10), show=False)
            uplot.plotCorrelation(stepBlock*timeStep, particleCorr[:,1], "$ISF(\\Delta t)$", "$time$ $interval,$ $\\Delta t$", logx = True, color=colorList(block/10), show=False)
            plt.pause(0.2)
        if(computeTau=="tau"):
            diff.append(np.mean(particleCorr[-20:,0]/(2*stepBlock[-20:]*timeStep)))
            ISF = particleCorr[:,1]
            step = stepBlock
            relStep = np.argwhere(ISF>np.exp(-1))[-1,0]
            if(relStep + 1 < step.shape[0]):
                t1 = step[relStep]
                t2 = step[relStep+1]
                ISF1 = ISF[relStep]
                ISF2 = ISF[relStep+1]
                slope = (ISF2 - ISF1)/(t2 - t1)
                intercept = ISF2 - slope * t2
                tau.append(timeStep*(np.exp(-1) - intercept)/slope)
            else:
                tau.append(timeStep*step[relStep])
    if(computeTau=="tau"):
        print("relaxation time: ", np.mean(tau), " +- ", np.std(tau))
        print("diffusivity: ", np.mean(diff), " +- ", np.std(diff))
        np.savetxt(dirName + "relaxationData.dat", np.array([[timeStep, phi, T, np.mean(tau), np.std(tau), np.mean(diff), np.std(diff)]]))

def collectRelaxationDataVSTemp(dirName):
    data = []
    TList = np.array(["0.03", "0.035", "0.037", "0.04", "0.045", "0.05", "0.055", "0.06", "0.065", "0.07", "0.08", "0.1", "0.11", "0.12", "0.13", "0.14", "0.15", "0.17", "0.18", "0.19", #1e08
                            "0.2", "0.23", "0.26", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1", "1.3", "1.6", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
    for i in range(TList.shape[0]):
        fileName = dirName + os.sep + "T" + TList[i] + os.sep + "dynamics/relaxationData.dat"
        if(os.path.exists(fileName)):
            data.append(np.loadtxt(fileName))
    np.savetxt(dirName + os.sep + "averageRelData.dat", data)

########### Time-averaged Self Correlations in log-spaced time window ##########
def computeParticleLogSelfCorr(dirName, startBlock, maxPower, freqPower, qFrac = 1, computeTau = "tau"):
    numParticles = ucorr.readFromParams(dirName, "numParticles")
    boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "particleRad.dat")))
    phi = ucorr.readFromParams(dirName, "phi")
    timeStep = ucorr.readFromParams(dirName, "dt")
    T = np.mean(np.loadtxt(dirName + "energy.dat")[:,4])
    #pWaveVector = 2 * np.pi / (2 * np.sqrt(boxSize[0] * boxSize[1] * phi / (np.pi * numParticles)))
    if(os.path.exists(dirName + os.sep + "pairCorr.dat")):
        pcorr = np.loadtxt(dirName + os.sep + "pairCorr.dat")
        firstPeak = pcorr[np.argmax(pcorr[:,1]),0]
        pWaveVector = 2 * np.pi / firstPeak
    else:
        pWaveVector = 2 * np.pi / (float(qFrac) * 2 * pRad)
    print("wave vector: ", pWaveVector, " meanRad: ", pRad)
    particleCorr = []
    stepList = []
    freqDecade = int(10**freqPower)
    decadeSpacing = 10
    spacingDecade = 1
    stepDecade = 10
    numBlocks = int(10**(maxPower-freqPower))
    for power in range(maxPower):
        for spacing in range(1,decadeSpacing):
            stepRange = np.arange(0,stepDecade,spacing*spacingDecade,dtype=int)
            #print(stepRange, spacing*spacingDecade)
            stepParticleCorr = []
            numPairs = 0
            for multiple in range(startBlock, numBlocks):
                for i in range(stepRange.shape[0]-1):
                    if(ucorr.checkPair(dirName, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])):
                        #print(multiple, i, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])
                        pPos1, pPos2 = ucorr.readParticlePair(dirName, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])
                        stepParticleCorr.append(ucorr.computeCorrFunctions(pPos1, pPos2, boxSize, pWaveVector, pRad**2))
                        numPairs += 1
            if(numPairs > 0):
                stepList.append(spacing*spacingDecade)
                particleCorr.append(np.mean(stepParticleCorr, axis=0))
        stepDecade *= 10
        spacingDecade *= 10
    stepList = np.array(stepList)
    particleCorr = np.array(particleCorr).reshape((stepList.shape[0],7))
    particleCorr = particleCorr[np.argsort(stepList)]
    np.savetxt(dirName + os.sep + "corr-log-q" + str(qFrac) + ".dat", np.column_stack((stepList, particleCorr)))
    print("diffusivity: ", np.mean(particleCorr[-20:,0]/(4*stepList[-20:]*timeStep)), " ", np.std(particleCorr[-20:,0]/(4*stepList[-20:]*timeStep)))
    #uplot.plotCorrelation(stepList * timeStep, particleCorr[:,0]/(stepList*timeStep), "$MSD(\\Delta t)/\\Delta t$", "$time$ $interval,$ $\\Delta t$", logx = True, color = 'r')
    uplot.plotCorrelation(stepList * timeStep, particleCorr[:,1], "$ISF(\\Delta t)$", "$time$ $interval,$ $\\Delta t$", logx = True, color = 'k')
    uplot.plotCorrelation(stepList * timeStep, particleCorr[:,3], "$ISF(\\Delta t)$", "$time$ $interval,$ $\\Delta t$", logx = True, color = 'r')
    if(computeTau=="tau"):
        diff = np.mean(particleCorr[-1:,0]/(2 * stepRange[-1:] * timeStep))
        ISF = particleCorr[:,1]
        step = stepList
        relStep = np.argwhere(ISF>np.exp(-1))[-1,0]
        if(relStep + 1 < step.shape[0]):
            t1 = step[relStep]
            t2 = step[relStep+1]
            ISF1 = ISF[relStep]
            ISF2 = ISF[relStep+1]
            slope = (ISF2 - ISF1)/(t2 - t1)
            intercept = ISF2 - slope * t2
            tau = timeStep*(np.exp(-1) - intercept)/slope
            print("relaxation time: ", tau)
        else:
            tau = 0
            print("not enough data to compute relaxation time")
        with open(dirName + "../../../tauDiff.dat", "ab") as f:
            np.savetxt(f, np.array([[timeStep, pWaveVector, phi, T, tau, diff]]))

########## Time-averaged Single Correlations in log-spaced time window #########
def computeSingleParticleLogSelfCorr(dirName, startBlock, maxPower, freqPower, qFrac = 1):
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "particleRad.dat")))
    phi = ucorr.readFromParams(dirName, "phi")
    timeStep = ucorr.readFromParams(dirName, "dt")
    T = np.mean(np.loadtxt(dirName + "energy.dat")[:,4])
    pWaveVector = 2 * np.pi / (float(qFrac) * 2 * pRad)
    print("wave vector: ", pWaveVector)
    particleCorr = []
    stepList = []
    freqDecade = int(10**freqPower)
    decadeSpacing = 10
    spacingDecade = 1
    stepDecade = 10
    numBlocks = int(10**(maxPower-freqPower))
    for power in range(maxPower):
        for spacing in range(1,decadeSpacing):
            stepRange = np.arange(0,stepDecade,spacing*spacingDecade,dtype=int)
            #print(stepRange, spacing*spacingDecade)
            stepParticleCorr = np.zeros(numParticles)
            numPairs = 0
            for multiple in range(startBlock, numBlocks):
                for i in range(stepRange.shape[0]-1):
                    if(ucorr.checkPair(dirName, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])):
                        #print(multiple, i, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])
                        pPos1, pPos2 = ucorr.readParticlePair(dirName, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])
                        stepParticleCorr += ucorr.computeSingleParticleISF(pPos1, pPos2, boxSize, pWaveVector, pRad**2)
                        numPairs += 1
            if(numPairs > 0):
                stepList.append(spacing*spacingDecade)
                particleCorr.append(stepParticleCorr/numPairs)
        stepDecade *= 10
        spacingDecade *= 10
    stepList = np.array(stepList)
    particleCorr = np.array(particleCorr).reshape((stepList.shape[0],numParticles))
    particleCorr = particleCorr[np.argsort(stepList)]
    tau = []
    step = stepList
    for i in range(0,numParticles,20):
        #uplot.plotCorrelation(stepList * timeStep, particleCorr[:,0]/(stepList*timeStep), "$MSD(\\Delta t)/\\Delta t$", "$time$ $interval,$ $\\Delta t$", logx = True, color = 'r')
        #uplot.plotCorrelation(stepList * timeStep, particleCorr[:,i], "$ISF(t)$", "$time$ $interval,$ $\\Delta t$", logx = True, color = 'r')
        ISF = particleCorr[:,i]
        relStep = np.argwhere(ISF>np.exp(-1))[-1,0]
        #tau.append(step[relStep] * timeStep)
        if(relStep + 1 < step.shape[0]):
            t1 = step[relStep]
            t2 = step[relStep+1]
            ISF1 = ISF[relStep]
            ISF2 = ISF[relStep+1]
            slope = (ISF2 - ISF1)/(t2 - t1)
            intercept = ISF2 - slope * t2
            tau.append(timeStep*(np.exp(-1) - intercept)/slope)
    print("mean relaxation time: ", np.mean(tau), ", std: ", np.std(tau))
    np.savetxt(dirName + "tauSingles.dat", np.array([[timeStep, pWaveVector, phi, T, np.mean(tau), np.var(tau), np.std(tau)]]))

def collectRelaxationDataVSPhi(dirName, dynName="langevin"):
    T = []
    diff = []
    tau = []
    deltaChi = []
    phiList = np.array(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])
    for i in range(phiList.shape[0]):
        dirSample = dirName + phiList[i] + os.sep + dynName + os.sep
        if(os.path.exists(dirSample)):
            dir = os.listdir(dirSample)
            if(os.path.exists(dirSample + dir + "/dynamics/corr-log-q1.dat")):
                timeStep = readFromParams(dirSample + dir + "/dynamics/", "dt")
                energy = np.loadtxt(dirName + dir + "/dynamics/energy.dat")
                T.append(np.mean(energy[:,4]))
                data = np.loadtxt(dirSample + dir + "/dynamics/corr-log-q1.dat")
                diff.append(data[-1,1]/(4 * data[-1,0] * timeStep))
                tau.append(timeStep*uplot.computeTau(data))
                deltaChi.append(timeStep*uplot.computeDeltaChi(data))
        np.savetxt(dirName + phiList[i] + "/relaxationData.dat", np.column_stack((T, diff, tau, deltaChi)))

############################## Local Temperature ###############################
def computeLocalTemperaturePDF(dirName, numBins, plot = False):
    boxSize = np.array(np.loadtxt(dirName + os.sep + "boxSize.dat"))
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    xbin = np.linspace(0, boxSize[0], numBins+1)
    ybin = np.linspace(0, boxSize[1], numBins+1)
    tempData = []
    numSamples = 0
    for dir in os.listdir(dirName):
        if(os.path.exists(dirName + os.sep + dir + os.sep + "particleRad.dat")):
            localEkin = np.zeros((numBins, numBins))
            pVel = np.array(np.loadtxt(dirName + os.sep + dir + os.sep + "particleVel.dat"))
            pPos = np.array(np.loadtxt(dirName + os.sep + dir + os.sep + "particlePos.dat"))
            Temp = np.mean(np.linalg.norm(pVel,axis=1)**2)
            pPos[:,0] -= np.floor(pPos[:,0]/boxSize[0]) * boxSize[0]
            pPos[:,1] -= np.floor(pPos[:,1]/boxSize[1]) * boxSize[1]
            ucorr.computeLocalTempGrid(pPos, pVel, xbin, ybin, localTemp)
            tempData.append(localTemp.flatten()/Temp)
    tempData = np.sort(tempData)
    cdf = np.arange(len(tempData))/len(tempData)
    pdf, edges = np.histogram(tempData, bins=np.linspace(np.min(tempData), np.max(tempData), 50), density=True)
    edges = (edges[:-1] + edges[1:])/2
    np.savetxt(dirName + os.sep + "localTemperature-N" + str(numBins) + ".dat", np.column_stack((edges, pdf)))
    if(plot=="plot"):
        fig = plt.figure(dpi=120)
        ax = plt.gca()
        ax.semilogy(edges[1:], pdf[1:], linewidth=1.2, color='k')
        #ax.plot(sampleDensity, cdf, linewidth=1.2, color='k')
        ax.tick_params(axis='both', labelsize=15)
        ax.set_ylabel('$P(T_{local})$', fontsize=18)
        ax.set_xlabel('$T_{local}$', fontsize=18)
        plt.tight_layout()
        plt.pause(1)
    mean = np.mean(tempData)
    var = np.var(tempData)
    print("data stats: ", np.min(tempData), np.max(tempData), mean, var)
    return mean, var, np.mean((tempData - np.mean(tempData))**4)/(3*var**2) - 1

def collectLocalTemperaturePDF(dirName, numBins, plot):
    dataSetList = np.array(["0.06", "0.07", "0.08", "0.09", "0.1", "0.11", "0.12", "0.13", "0.14", "0.15", "0.16", "0.17", "0.18", "0.19",
                            "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
    data = np.zeros((dataSetList.shape[0], 3))
    for i in range(dataSetList.shape[0]):
        dirSample = dirName + "/T" + dataSetList[i] + "/dynamics/"
        if(os.path.exists(dirSample + os.sep + "t0/params.dat")):
            data[i] = computeLocalTemperaturePDF(dirSample, numBins, plot)
    np.savetxt(dirName + "temperatureData-N" + numBins + ".dat", data)

########################### Hexitic Order Parameter ############################
def computeHexaticOrder(dirName, boxSize):
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    pPos = np.array(np.loadtxt(dirName + os.sep + "particlePos.dat"))
    contacts = np.array(np.loadtxt(dirName + os.sep + "contacts.dat"), dtype = int)
    psi6 = np.zeros(numParticles)
    for i in range(numParticles):
        numContacts = 0
        for c in range(contacts[i].shape[0]):
            if(contacts[i,c] != -1):
                numContacts += 1
                delta = ucorr.pbcDistance(pPos[i], pPos[contacts[i,c]], boxSize)
                theta = np.arctan2(delta[1], delta[0])
                psi6[i] += np.exp(6j*theta)
        if(numContacts > 0):
            psi6[i] /= numContacts
            psi6[i] = np.abs(psi6[i])
    return psi6

########################## Hexitic Order Correlation ###########################
def computeHexaticCorrelation(dirName, boxSize):
    pPos = np.array(np.loadtxt(dirName + os.sep + "particlePos.dat"))
    psi6 = computeHexaticOrder(dirName)
    distance = ucorr.computeDistances(pPos, boxSize) / boxSize[0]
    bins = np.linspace(np.min(distance[distance>0]), np.max(distance), 50)
    binCenter = 0.5 * (bins[:-1] + bins[1:])
    hexCorr = np.zeros(binCenter.shape[0])
    counts = np.zeros(binCenter.shape[0])
    for i in range(1,pPos.shape[0]):
        for j in range(i):
            for k in range(bins.shape[0]-1):
                if(distance[i,j] > bins[k] and distance[i,j] <= bins[k+1]):
                    hexCorr[k] += psi6[i] * np.conj(psi6[j])
                    counts[k] += 1
    hexCorr /= counts
    return binCenter, hexCorr

############################ Velocity correlations #############################
def computeParticleVelPDF(dirName, plot=True):
    vel = []
    for dir in os.listdir(dirName):
        if(os.path.isdir(dirName + os.sep + dir)):
            vel.append(np.loadtxt(dirName + os.sep + dir + os.sep + "particleVel.dat"))
    vel = np.array(vel).flatten()
    mean = np.mean(vel)
    Temp = np.var(vel)
    skewness = np.mean((vel - mean)**3)/Temp**(3/2)
    kurtosis = np.mean((vel - mean)**4)/Temp**2
    vel /= np.sqrt(2*Temp)
    velPDF, edges = np.histogram(vel, bins=np.linspace(np.min(vel), np.max(vel), 100), density=True)
    edges = 0.5 * (edges[:-1] + edges[1:])
    print("Variance of the velocity pdf: ", Temp, " kurtosis: ", kurtosis, " skewness: ", skewness)
    uplot.plotCorrelation(edges, velPDF, "$Velocity$ $distribution,$ $P(c)$", logy = True)

def computeParticleVelPDFSubSet(dirName, firstIndex=10, mass=1e06, plot="plot"):
    vel = []
    velSubSet = []
    temp = []
    tempSubSet = []
    var = []
    varSubSet = []
    step = []
    numParticles = ucorr.readFromParams(dirName + os.sep + "t0", "numParticles")
    nDim = 2
    for dir in os.listdir(dirName):
        if(os.path.isdir(dirName + os.sep + dir)):
            pVel = np.loadtxt(dirName + os.sep + dir + os.sep + "particleVel.dat")
            vel.append(pVel[firstIndex:,:])
            subset = pVel[:firstIndex,:] * np.sqrt(mass)
            velSubSet.append(subset)
            temp.append(np.sum(pVel[firstIndex:,:]**2)/((numParticles - firstIndex)*nDim))
            tempSubSet.append(np.sum(subset**2)/(firstIndex*nDim))
            var.append(np.var(pVel[firstIndex:,:]))
            varSubSet.append(np.var(subset))
            step.append(float(dir[1:]))
    vel = np.array(vel).flatten()
    velSubSet = np.array(velSubSet).flatten()
    temp = np.array(temp)
    tempSubSet = np.array(tempSubSet)
    temp = temp[np.argsort(step)]
    tempSubSet = tempSubSet[np.argsort(step)]
    var = np.array(var)
    varSubSet = np.array(varSubSet)
    var = var[np.argsort(step)]
    varSubSet = varSubSet[np.argsort(step)]
    step = np.sort(step)
    #velSubSet /= np.sqrt(2*np.var(velSubSet))
    velBins = np.linspace(np.min(velSubSet), np.max(velSubSet), 30)
    velPDF, edges = np.histogram(vel, bins=velBins, density=True)
    velSubSetPDF, edges = np.histogram(velSubSet, bins=velBins, density=True)
    edges = 0.5 * (edges[:-1] + edges[1:])
    np.savetxt(dirName + os.sep + "velocityPDF.dat", np.column_stack((edges, velPDF, velSubSetPDF)))
    #print("Variance of the velocity pdf:", np.var(vel), " variance of the subset velocity pdf: ", np.var(velSubSet))
    if(plot=="plot"):
        uplot.plotCorrelation(edges, velPDF / np.sqrt(mass), "$Velocity$ $distribution,$ $P(v)$", xlabel = "$Velocity,$ $v$", logy = True)
    return np.var(vel), np.var(velSubSet)

##################### Particle Self Velocity Correlations ######################
def computeParticleVelTimeCorr(dirName):
    numParticles = ucorr.readFromParams(dirName, "numParticles")
    timeStep = ucorr.readFromParams(dirName, "dt")
    particleVelCorr = []
    particleVelVar = []
    # get trajectory directories
    stepRange = ucorr.getDirectories(dirName)
    stepRange = np.array(np.char.strip(stepRange, 't'), dtype=int)
    stepRange = np.sort(stepRange)
    pVel0 = np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[0]) + "/particleVel.dat"))
    pVel0Squared = np.mean(np.linalg.norm(pVel0,axis=1)**2)/2
    for i in range(0,stepRange.shape[0]):
        pVel = np.array(np.loadtxt(dirName + os.sep + "t" + str(stepRange[i]) + "/particleVel.dat"))
        particleVelCorr.append(np.mean(np.multiply(pVel,pVel0)))
        meanVel = np.mean(pVel, axis=0)
        particleVelVar.append(np.mean((pVel - meanVel)**2))
    particleVelCorr /= pVel0Squared
    np.savetxt(dirName + os.sep + "velCorr.dat", np.column_stack(((stepRange+1)*timeStep, particleVelCorr, particleVelVar)))
    uplot.plotCorrelation((stepRange + 1) * timeStep, particleVelCorr, "$C_{vv}(\\Delta t)$", "$Time$ $interval,$ $\\Delta t$", color='k')
    uplot.plotCorrelation((stepRange + 1) * timeStep, particleVelVar, "$\\langle \\vec{v}(t) - \\langle \\vec{v}(t) \\rangle \\rangle$", "$Simulation$ $time$", color='r')
    width = stepRange[np.argwhere(particleVelCorr/particleVelCorr[0] < np.exp(-1))[0,0]]*timeStep
    print("Measured damping coefficient: ", 1/width)
    plt.show()

##################### Particle Self Velocity Correlations ######################
def computeParticleBlockVelTimeCorr(dirName, numBlocks):
    numParticles = ucorr.readFromParams(dirName, "numParticles")
    timeStep = ucorr.readFromParams(dirName, "dt")
    # get trajectory directories
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    blockFreq = dirList.shape[0]//numBlocks
    timeList = timeList[:blockFreq]
    blockVelCorr = np.zeros((blockFreq, numBlocks))
    blockVelVar = np.zeros((blockFreq, numBlocks))
    for block in range(numBlocks):
        pVel0 = np.array(np.loadtxt(dirName + os.sep + dirList[block*blockFreq] + "/particleVel.dat"))
        pVel0Squared = np.mean(np.linalg.norm(pVel0,axis=1)**2)/2
        for i in range(blockFreq):
            pVel = np.array(np.loadtxt(dirName + os.sep + dirList[block*blockFreq + i] + "/particleVel.dat"))
            blockVelCorr[i, block] = np.mean(np.multiply(pVel,pVel0))
            meanVel = np.mean(pVel, axis=0)
            blockVelVar[i, block] = np.mean((pVel - meanVel)**2)
        blockVelCorr[:, block] /= pVel0Squared
    particleVelCorr = np.column_stack((np.mean(blockVelCorr, axis=1), np.std(blockVelCorr, axis=1)))
    particleVelVar = np.mean(blockVelVar, axis=1)
    np.savetxt(dirName + os.sep + "blockVelCorr.dat", np.column_stack((timeList * timeStep, particleVelCorr, particleVelVar)))
    uplot.plotCorrelation(timeList * timeStep, particleVelCorr[:,0], "$C_{vv}(\\Delta t)$", "$Time$ $interval,$ $\\Delta t$", color='k')
    uplot.plotCorrelation(timeList * timeStep, particleVelVar, "$\\langle \\vec{v}(t) - \\langle \\vec{v}(t) \\rangle \\rangle$", "$Simulation$ $time$", color='r')
    width = timeList[np.argwhere(particleVelCorr/particleVelCorr[0] < np.exp(-1))[0,0]]*timeStep
    print("Measured damping coefficient: ", 1/width)
    #plt.show()

############# Time-averaged Self Vel Corr in log-spaced time window ############
def computeParticleLogVelTimeCorr(dirName, startBlock, maxPower, freqPower):
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    timeStep = ucorr.readFromParams(dirName, "dt")
    #pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "/particleRad.dat")))
    #phi = ucorr.readFromParams(dirName, "phi")
    #waveVector = np.pi / (2 * np.sqrt(boxSize[0] * boxSize[1] * phi / (np.pi * numParticles)))
    #pRad = np.mean(np.array(np.loadtxt(dirName + os.sep + "particleRad.dat")))
    #waveVector = np.pi / (float(radMultiple) * pRad)
    particleVelCorr = []
    particleDirCorr = []
    stepList = []
    freqDecade = int(10**freqPower)
    decadeSpacing = 10
    spacingDecade = 1
    stepDecade = 10
    numBlocks = int(10**(maxPower-freqPower))
    for power in range(maxPower):
        for spacing in range(1,decadeSpacing):
            stepRange = np.arange(0,stepDecade,spacing*spacingDecade,dtype=int)
            stepParticleVelCorr = []
            stepParticleDirCorr = []
            numPairs = 0
            for multiple in range(startBlock, numBlocks):
                for i in range(stepRange.shape[0]-1):
                    if(ucorr.checkPair(dirName, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])):
                        pVel1, pVel2 = ucorr.readVelPair(dirName, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])
                        #pPos1, pPos2 = ucorr.readParticlePair(dirName, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])
                        pDir1, pDir2 = ucorr.readDirectorPair(dirName, multiple*freqDecade + stepRange[i], multiple*freqDecade + stepRange[i+1])
                        #stepParticleVelCorr.append(ucorr.computeVelCorrFunctions(pPos1, pPos2, pVel1, pVel2, pDir1, pDir2, waveVector, numParticles))
                        stepParticleVelCorr.append(np.mean(np.sum(np.multiply(pVel1,pVel2), axis=1)))
                        stepParticleDirCorr.append(np.mean(np.sum(np.multiply(pDir1,pDir2), axis=1)))
                        numPairs += 1
            if(numPairs > 0):
                stepList.append(spacing*spacingDecade)
                particleVelCorr.append([np.mean(stepParticleVelCorr, axis=0), np.std(stepParticleVelCorr, axis=0)])
                particleDirCorr.append([np.mean(stepParticleDirCorr, axis=0), np.std(stepParticleDirCorr, axis=0)])
        stepDecade *= 10
        spacingDecade *= 10
    stepList = np.array(stepList)
    particleVelCorr = np.array(particleVelCorr).reshape((stepList.shape[0],2))
    particleVelCorr = particleVelCorr[np.argsort(stepList)]
    particleDirCorr = np.array(particleDirCorr).reshape((stepList.shape[0],2))
    particleDirCorr = particleDirCorr[np.argsort(stepList)]
    np.savetxt(dirName + os.sep + "logVelCorr.dat", np.column_stack((stepList*timeStep, particleVelCorr)))
    np.savetxt(dirName + os.sep + "logDirCorr.dat", np.column_stack((stepList*timeStep, particleDirCorr)))
    uplot.plotCorrWithError(stepList*timeStep, particleVelCorr[:,0], particleVelCorr[:,1], ylabel="$C_{vv}(\\Delta t)$", logx = True, color = 'k')
    uplot.plotCorrWithError(stepList*timeStep, particleDirCorr[:,0], particleDirCorr[:,1], ylabel="$C_{nn}(\\Delta t)$", logx = True, color = 'r')
    #plt.show()

############################# Velocity Correlation #############################
def computeParticleVelSpaceCorr(dirName):
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    boxSize = np.array(np.loadtxt(dirName + os.sep + "boxSize.dat"))
    minRad = np.min(np.loadtxt(dirName + os.sep + "particleRad.dat"))
    pos = np.array(np.loadtxt(dirName + os.sep + "particlePos.dat"))
    distance = ucorr.computeDistances(pos, boxSize)
    bins = np.arange(2*minRad, np.sqrt(2)*boxSize[0]/2, 2*minRad)
    vel = np.array(np.loadtxt(dirName + os.sep + "particleVel.dat"))
    velNorm = np.linalg.norm(vel, axis=1)
    velNormSquared = np.mean(velNorm**2)
    velCorr = np.zeros((bins.shape[0]-1,4))
    counts = np.zeros(bins.shape[0]-1)
    for i in range(distance.shape[0]):
        for j in range(i):
            for k in range(bins.shape[0]-1):
                if(distance[i,j] > bins[k] and distance[i,j] <= bins[k+1]):
                    # parallel
                    delta = ucorr.pbcDistance(pos[i], pos[j], boxSize)/distance[i,j]
                    parProj1 = np.dot(vel[i],delta)
                    parProj2 = np.dot(vel[j],delta)
                    # perpendicular
                    deltaPerp = np.array([-delta[1], delta[0]])
                    perpProj1 = np.dot(vel[i],deltaPerp)
                    perpProj2 = np.dot(vel[j],deltaPerp)
                    # correlations
                    velCorr[k,0] += parProj1 * parProj2
                    velCorr[k,1] += perpProj1 * perpProj2
                    velCorr[k,2] += (perpProj1 * parProj2 + parProj1 * perpProj2)*0.5
                    velCorr[k,3] += np.dot(vel[i],vel[j])
                    counts[k] += 1
    binCenter = (bins[1:] + bins[:-1])/2
    for i in range(velCorr.shape[1]):
        velCorr[counts>0,i] /= counts[counts>0]
    velCorr /= velNormSquared
    np.savetxt(dirName + os.sep + "spaceVelCorr1.dat", np.column_stack((binCenter, velCorr, counts)))
    uplot.plotCorrelation(binCenter, velCorr[:,0], "$C_{vv}(r)$", "$Distance,$ $r$", color = 'r')
    uplot.plotCorrelation(binCenter, velCorr[:,1], "$C_{vv}(r)$", "$Distance,$ $r$", color = 'g')
    uplot.plotCorrelation(binCenter, velCorr[:,2], "$C_{vv}(r)$", "$Distance,$ $r$", color = 'k')
    plt.show()

############################# Velocity Correlation #############################
def averageParticleVelSpaceCorr(dirName, dirSpacing=1000):
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    boxSize = np.array(np.loadtxt(dirName + os.sep + "boxSize.dat"))
    minRad = np.min(np.loadtxt(dirName + os.sep + "particleRad.dat"))
    bins = np.arange(2*minRad, np.sqrt(2)*boxSize[0]/2, 2*minRad)
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    timeList = timeList.astype(int)
    dirList = dirList[np.argwhere(timeList%dirSpacing==0)[:,0]]
    dirList = dirList[-50:]
    velCorr = np.zeros((bins.shape[0]-1,4))
    counts = np.zeros(bins.shape[0]-1)
    for d in range(dirList.shape[0]):
        pos = np.array(np.loadtxt(dirName + os.sep + dirList[d] + os.sep + "particlePos.dat"))
        distance = ucorr.computeDistances(pos, boxSize)
        vel = np.array(np.loadtxt(dirName + os.sep + dirList[d] + os.sep + "particleVel.dat"))
        velNorm = np.linalg.norm(vel, axis=1)
        vel[:,0] /= velNorm
        vel[:,1] /= velNorm
        velNormSquared = np.mean(velNorm**2)
        for i in range(distance.shape[0]):
            for j in range(i):
                    for k in range(bins.shape[0]-1):
                        if(distance[i,j] > bins[k] and distance[i,j] <= bins[k+1]):
                            # parallel
                            delta = ucorr.pbcDistance(pos[i], pos[j], boxSize)/distance[i,j]
                            parProj1 = np.dot(vel[i],delta)
                            parProj2 = np.dot(vel[j],delta)
                            velCorr[k,0] += parProj1 * parProj2
                            # perpendicular
                            deltaPerp = np.array([-delta[1], delta[0]])
                            perpProj1 = np.dot(vel[i],deltaPerp)
                            perpProj2 = np.dot(vel[j],deltaPerp)
                            velCorr[k,1] += perpProj1 * perpProj2
                            # off-diagonal
                            velCorr[k,2] += (perpProj1 * parProj2 + parProj1 * perpProj2)*0.5
                            # total
                            velCorr[k,3] += np.dot(vel[i],vel[j])
                            counts[k] += 1
    for i in range(velCorr.shape[1]):
        velCorr[counts>0,i] /= counts[counts>0]
    #velCorr /= velNormSquared
    binCenter = (bins[1:] + bins[:-1])/2
    np.savetxt(dirName + os.sep + "spaceVelCorr.dat", np.column_stack((binCenter, velCorr, counts)))
    uplot.plotCorrelation(binCenter, velCorr[:,0], "$C_{vv}(r)$", "$Distance,$ $r$", color = 'r')
    uplot.plotCorrelation(binCenter, velCorr[:,1], "$C_{vv}(r)$", "$Distance,$ $r$", color = 'g')
    uplot.plotCorrelation(binCenter, velCorr[:,2], "$C_{vv}(r)$", "$Distance,$ $r$", color = 'k')
    plt.show()

########################### Average Space Correlator ###########################
def averagePairCorr(dirName, dirSpacing=1):
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    phi = ucorr.readFromParams(dirName, "phi")
    boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    minRad = np.mean(np.loadtxt(dirName + os.sep + "particleRad.dat"))
    rbins = np.arange(0, np.sqrt(2)*boxSize[0]/2, 0.05*minRad)
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    timeList = timeList.astype(int)
    dirList = dirList[np.argwhere(timeList%dirSpacing==0)[:,0]]
    print(dirList.shape[0])
    pcorr = np.zeros(rbins.shape[0]-1)
    for dir in dirList:
        #pos = np.array(np.loadtxt(dirName + os.sep + dir + "/particlePos.dat"))
        pos = ucorr.getPBCPositions(dirName + os.sep + dir + "/particlePos.dat", boxSize)
        pcorr += ucorr.getPairCorr(pos, boxSize, rbins, minRad)/(numParticles * phi)
    pcorr[pcorr>0] /= dirList.shape[0]
    binCenter = (rbins[:-1] + rbins[1:])*0.5
    firstPeak = binCenter[np.argmax(pcorr)]
    np.savetxt(dirName + os.sep + "pairCorr.dat", np.column_stack((binCenter, pcorr)))
    print("First peak of pair corr is at distance:", firstPeak, "equal to", firstPeak/minRad, "times the min radius:", minRad)
    np.savetxt(dirName + os.sep + "pcorrFirstPeak.dat", np.column_stack((firstPeak, np.max(pcorr))))
    uplot.plotCorrelation(binCenter/minRad, pcorr, "$g(r/\\sigma)$", "$r/\\sigma$")
    #plt.show()

########################### Average Space Correlator ###########################
def getCollisionIntervalPDF(dirName, check=False, numBins=40):
    timeStep = ucorr.readFromParams(dirName, "dt")
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    if(os.path.exists(dirName + "/collisionIntervals.dat") and check=="check"):
        interval = np.loadtxt(dirName + os.sep + "collisionIntervals.dat")
    else:
        interval = np.empty(0)
        previousTime = np.zeros(numParticles)
        previousVel = np.array(np.loadtxt(dirName + os.sep + "t0/particleVel.dat"))
        for i in range(1,dirList.shape[0]):
            currentTime = timeList[i]
            currentVel = np.array(np.loadtxt(dirName + os.sep + dirList[i] + "/particleVel.dat"), dtype=np.float64)
            colIndex = np.argwhere(currentVel[:,0]!=previousVel[:,0])[:,0]
            currentInterval = currentTime-previousTime[colIndex]
            interval = np.append(interval, currentInterval[currentInterval>1])
            previousTime[colIndex] = currentTime
            previousVel = currentVel
        interval = np.sort(interval)
        interval = interval[interval>10]
        interval *= timeStep
        #np.savetxt(dirName + os.sep + "collisionIntervals.dat", interval)
    bins = np.linspace(np.min(interval), np.max(interval), numBins)
    pdf, edges = np.histogram(interval, bins=bins, density=True)
    centers = (edges[1:] + edges[:-1])/2
    print("average collision time:", np.mean(interval), " standard deviation: ", np.std(interval))
    np.savetxt(dirName + os.sep + "collision.dat", np.column_stack((centers, pdf)))
    uplot.plotCorrelation(centers, pdf, "$PDF(\\Delta_c)$", "$Time$ $between$ $collisions,$ $\\Delta_c$", logy=True)
    plt.show()

########################### Average Space Correlator ###########################
def getContactCollisionIntervalPDF(dirName, check=False, spacing=100):
    timeStep = ucorr.readFromParams(dirName, "dt")
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    if(os.path.exists(dirName + "/contactCollisionIntervals.dat") and check=="check"):
        interval = np.loadtxt(dirName + os.sep + "contactCollisionIntervals.dat")
    else:
        interval = np.empty(0)
        previousTime = np.zeros(numParticles)
        previousContacts = np.array(np.loadtxt(dirName + os.sep + "t0/particleContacts.dat"))
        for i in range(1,dirList.shape[0]):
            currentTime = timeList[i]
            currentContacts = np.array(np.loadtxt(dirName + os.sep + dirList[i] + "/particleContacts.dat"), dtype=np.int64)
            colIndex = np.argwhere(currentContacts[:,0]!=previousContacts[:,0])[:,0]
            currentInterval = currentTime-previousTime[colIndex]
            interval = np.append(interval, currentInterval[currentInterval>1])
            previousTime[colIndex] = currentTime
            previousContacts = currentContacts
        interval = np.sort(interval)
        interval = interval[interval>10]
        interval *= timeStep
        np.savetxt(dirName + os.sep + "contactCollisionIntervals.dat", interval)
    bins = np.arange(np.min(interval), np.max(interval), spacing*timeStep)
    #bins = np.linspace(np.min(interval), np.max(interval), spacing)
    pdf, edges = np.histogram(interval, bins=bins, density=True)
    centers = (edges[1:] + edges[:-1])/2
    print("average collision time:", np.mean(interval), " standard deviation: ", np.std(interval))
    np.savetxt(dirName + os.sep + "contactCollision.dat", np.column_stack((centers, pdf)))
    centers = centers[np.argwhere(pdf>0)[:,0]]
    pdf = pdf[pdf>0]
    uplot.plotCorrelation(centers, pdf, "$PDF(\\Delta_c)$", "$Time$ $between$ $collisions,$ $\\Delta_c$", logy=True)
    #plt.xlim(-500*timeStep, timeList[-1]*timeStep)
    #cdf = np.arange(len(interval))/len(interval)
    #indices = (np.unique(np.geomspace(1, len(interval), num=100, dtype=int)) - 1)
    #interval = interval[indices]
    #cdf = cdf[indices]
    #uplot.plotCorrelation(interval, cdf, "$CDF(\\Delta_c)$", "$Collision$ $time,$ $\\Delta_c$", logy=True, logx=True)
    #plt.show()

def computeActivePressure(dirName, plot=False):
    driving = float(ucorr.readFromDynParams(dirName, "f0"))
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    energy = np.loadtxt(dirName + os.sep + "energy.dat")
    timeStep = ucorr.readFromParams(dirName, "dt")
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    activePressure = np.zeros(dirList.shape[0])
    for i in range(dirList.shape[0]):
        pos = np.loadtxt(dirName + os.sep + dirList[i] + "/particlePos.dat")
        force = np.loadtxt(dirName + os.sep + dirList[i] + "/particleForces.dat")
        angle = np.loadtxt(dirName + os.sep + dirList[i] + "/particleAngles.dat")
        dir = driving*np.array([np.cos(angle), np.sin(angle)]).T
        activePressure[i] = np.sum(np.sum(dir*pos,axis=1))
    if(plot=='plot'):
        uplot.plotCorrelation(energy[:,0], energy[:,6], "$Pressure$", "$Time,$ $t$")
        uplot.plotCorrelation(timeList*timeStep, activePressure, "$Active$ $pressure$", "$Time,$ $t$")
        plt.show()
    return activePressure

############################ Local Packing Fraction ############################
def computeLocalDensity(dirName, numBins, plot = False):
    boxSize = np.array(np.loadtxt(dirName + os.sep + "boxSize.dat"))
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    rad = np.array(np.loadtxt(dirName + os.sep + "particleRad.dat"))
    pos = np.array(np.loadtxt(dirName + os.sep + "particlePos.dat"))
    pos[:,0] -= np.floor(pos[:,0]/boxSize[0]) * boxSize[0]
    pos[:,1] -= np.floor(pos[:,1]/boxSize[1]) * boxSize[1]
    xbin = np.linspace(0, boxSize[0], numBins+1)
    ybin = np.linspace(0, boxSize[1], numBins+1)
    localArea = np.zeros((numBins, numBins))
    localSquare = (boxSize[0]/numBins)*(boxSize[1]/numBins)
    ucorr.computeLocalAreaGrid(pos, rad, xbin, ybin, localArea)
    localDensity = localArea/localSquare
    localDensity = np.sort(localDensity.flatten())
    cdf = np.arange(len(localDensity))/len(localDensity)
    pdf, edges = np.histogram(localDensity, bins=np.linspace(np.min(localDensity), np.max(localDensity), 30), density=True)
    edges = (edges[1:] + edges[:-1])/2
    if(plot=="plot"):
        #print("subBoxSize: ", xbin[1]-xbin[0], ybin[1]-ybin[0], " lengthscale: ", np.sqrt(np.mean(area)))
        print("data stats: ", np.min(localDensity), np.max(localDensity), np.mean(localDensity), np.std(localDensity))
        fig = plt.figure(dpi=120)
        ax = plt.gca()
        ax.plot(edges[1:], pdf[1:], linewidth=1.2, color='k')
        #ax.plot(localDensity, cdf, linewidth=1.2, color='k')
        ax.tick_params(axis='both', labelsize=15)
        ax.set_ylabel('$P(\\varphi)$', fontsize=18)
        ax.set_xlabel('$\\varphi$', fontsize=18)
        #ax.set_xlim(-0.02, 1.02)
        plt.tight_layout()
        #plt.show()
    else:
        return localDensity

def averageLocalDensity(dirName, numBins=12, dirSpacing=1000):
    boxSize = np.array(np.loadtxt(dirName + os.sep + "boxSize.dat"))
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    timeStep = ucorr.readFromParams(dirName, "dt")
    xbin = np.linspace(0, boxSize[0], numBins+1)
    ybin = np.linspace(0, boxSize[1], numBins+1)
    localSquare = (boxSize[0]/numBins)*(boxSize[1]/numBins)
    rad = np.array(np.loadtxt(dirName + os.sep + "particleRad.dat"))
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    timeList = timeList.astype(int)
    dirList = dirList[np.argwhere(timeList%dirSpacing==0)[:,0]]
    #dirList = dirList[-50:]
    localDensity = []
    for dir in dirList:
        localArea = np.zeros((numBins, numBins))
        pos = ucorr.getPBCPositions(dirName + os.sep + dir + "/particlePos.dat", boxSize)
        ucorr.computeLocalAreaGrid(pos, rad, xbin, ybin, localArea)
        localDensity.append(localArea/localSquare)
    localDensity = np.array(localDensity).flatten()
    pdf, edges = np.histogram(localDensity, bins=np.linspace(np.min(localDensity), np.max(localDensity), 50), density=True)
    edges = (edges[:-1] + edges[1:])/2
    np.savetxt(dirName + os.sep + "localDensity-N" + str(numBins) + ".dat", np.column_stack((edges, pdf)))
    #mean = np.mean(sampleDensity)
    #var = np.var(sampleDensity)
    #skewness = np.mean((sampleDensity - np.mean(sampleDensity))**4)/(3*var**2) - 1
    uplot.plotCorrelation(edges, pdf, "$Local$ $density$", "$Time,$ $t$")
    #plt.show()

def localDensityVarianceVSTime(dirName, numBins=12):
    boxSize = np.array(np.loadtxt(dirName + os.sep + "boxSize.dat"))
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    timeStep = ucorr.readFromParams(dirName, "dt")
    xbin = np.linspace(0, boxSize[0], numBins+1)
    ybin = np.linspace(0, boxSize[1], numBins+1)
    localSquare = (boxSize[0]/numBins)*(boxSize[1]/numBins)
    rad = np.array(np.loadtxt(dirName + os.sep + "t0/particleRad.dat"))
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    localDensityVar = []
    for dir in dirList:
        localArea = np.zeros((numBins, numBins))
        pos = ucorr.getPBCPositions(dirName + os.sep + dir + "/particlePos.dat", boxSize)
        ucorr.computeLocalAreaGrid(pos, pRad, xbin, ybin, localArea)
        localDensity = localArea/localSquare
        localDensityVar.append(np.std(localDensity)/np.mean(localDensity))
    np.savetxt(dirName + "localDensityVarVSTime" + str(numBins) + ".dat", np.column_stack((timeList*timeStep, localDensityVar)))
    uplot.plotCorrelation(timeList*timeStep, localDensityVar, "$Variance$ $of$ $local$ $density$", "$Time,$ $t$")
    plt.show()

######################### Cluster Velocity Correlation #########################
def searchClusters(dirName, numParticles=None, plot=False, cluster="cluster"):
    if(numParticles==None):
        numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    contacts = np.array(np.loadtxt(dirName + os.sep + "particleContacts.dat"), dtype=int)
    particleLabel = np.zeros(numParticles)
    connectLabel = np.zeros(numParticles)
    noClusterList = np.zeros(numParticles)
    clusterLabel = 0
    for i in range(1,numParticles):
        if(np.sum(contacts[i]!=-1)>2):
            if(particleLabel[i] == 0): # this means it hasn't been checked yet
                # check that it is not a contact of contacts of previously checked particles
                belongToCluster = False
                for j in range(i):
                    for c in contacts[j, np.argwhere(contacts[j]!=-1)[:,0]]:
                        if(i==c):
                            # a contact of this particle already belongs to a cluster
                            particleLabel[i] = particleLabel[j]
                            belongToCluster = True
                            break
                if(belongToCluster == False):
                    newCluster = False
                    for c in contacts[i, np.argwhere(contacts[i]!=-1)[:,0]]:
                        if(np.sum(contacts[c]!=-1)>2 and newCluster == False):
                            newCluster = True
                    if(newCluster == True):
                        clusterLabel += 1
                        particleLabel[i] = clusterLabel
                        particleLabel[contacts[i, np.argwhere(contacts[i]!=-1)[:,0]]] = particleLabel[i]
        else:
            particleLabel[i] = 0
    # more stringent condition on cluster belonging
    connectLabel[np.argwhere(particleLabel > 0)] = 1
    for i in range(numParticles):
        connected = False
        for c in contacts[i, np.argwhere(contacts[i]!=-1)[:,0]]:
            if(particleLabel[c] != 0 and connected == False):
                connectLabel[i] = 1
                connected = True
        #connectLabel[contacts[i, np.argwhere(contacts[i]!=-1)[:,0]]] = 1
    # get cluster lengthscale, center
    rad = np.loadtxt(dirName + os.sep + "../particleRad.dat")
    NpInCluster = connectLabel[connectLabel!=0].shape[0]
    clusterSize = np.sqrt(NpInCluster) * np.mean(rad[connectLabel!=0])
    pos = np.loadtxt(dirName + os.sep + "particlePos.dat")
    boxSize = np.loadtxt(dirName + os.sep + "../boxSize.dat")
    pos[:,0] -= np.floor(pos[:,0]/boxSize[0]) * boxSize[0]
    pos[:,1] -= np.floor(pos[:,1]/boxSize[1]) * boxSize[1]
    clusterPos = np.mean(pos[connectLabel!=0], axis=0)
    # get list of particles within half of the lengthscale from the center
    deepList = np.zeros(numParticles)
    for i in range(numParticles):
        if(particleLabel[i] == 0 and np.sum(contacts[i]) < 2):
            noClusterList[i] = 1
        delta = ucorr.pbcDistance(pos[i], clusterPos, boxSize)
        distance = np.linalg.norm(delta)
        if(distance < clusterSize * 0.5 and connectLabel[i] == 1):
            deepList[i] = 1
    np.savetxt(dirName + "/deepList.dat", deepList)
    np.savetxt(dirName + "/noClusterList.dat", noClusterList)
    np.savetxt(dirName + "/clusterList.dat", np.column_stack((particleLabel, connectLabel)))
    if(plot=="plot"):
        print("Cluster position, x: ", clusterPos[0], " y: ", clusterPos[1])
        print("Cluster size: ", clusterSize)
        print("Number of clusters: ", clusterLabel)
        print("Number of particles in clusters: ", connectLabel[connectLabel!=0].shape[0])
        # plot packing
        boxSize = np.loadtxt(dirName + os.sep + "../boxSize.dat")
        pos = np.array(np.loadtxt(dirName + os.sep + "particlePos.dat"))
        rad = np.array(np.loadtxt(dirName + os.sep + "../particleRad.dat"))
        xBounds = np.array([0, boxSize[0]])
        yBounds = np.array([0, boxSize[1]])
        pos[:,0] -= np.floor(pos[:,0]/boxSize[0]) * boxSize[0]
        pos[:,1] -= np.floor(pos[:,1]/boxSize[1]) * boxSize[1]
        fig = plt.figure(0, dpi = 150)
        ax = fig.gca()
        ax.set_xlim(xBounds[0], xBounds[1])
        ax.set_ylim(yBounds[0], yBounds[1])
        ax.set_aspect('equal', adjustable='box')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])
        colorList = cm.get_cmap('prism', clusterLabel)
        colorId = np.zeros((pos.shape[0], 4))
        for i in range(numParticles):
            if(particleLabel[i]==0):
                colorId[i] = [1,1,1,1]
            else:
                colorId[i] = colorList(particleLabel[i]/clusterLabel)
        for particleId in range(numParticles):
            x = pos[particleId,0]
            y = pos[particleId,1]
            r = rad[particleId]
            ax.add_artist(plt.Circle([x, y], r, edgecolor='k', facecolor=[1,1,1], alpha=0.6, linewidth=0.5))
            if(cluster=="cluster"):
                ax.add_artist(plt.Circle([x, y], r, edgecolor='k', facecolor=colorId[particleId], alpha=0.6, linewidth=0.5))
                if(connectLabel[particleId] == 1):
                    ax.add_artist(plt.Circle([x, y], r, edgecolor='k', facecolor='k', alpha=0.3, linewidth=0.5))
            if(cluster=="deep" and deepList[particleId] == 1):
                ax.add_artist(plt.Circle([x, y], r, edgecolor='k', facecolor='k', alpha=0.6, linewidth=0.5))
            if(cluster=="nocluster" and noClusterList[particleId] == 1):
                ax.add_artist(plt.Circle([x, y], r, edgecolor='k', facecolor='k', alpha=0.6, linewidth=0.5))
        plt.show()
    if(cluster=="deep"):
        return deepList
    elif(cluster=="nocluster"):
        return noClusterList
    elif(cluster=="cluster"):
        return connectLabel

##################### Velocity Correlation in/out Cluster ######################
def averageParticleVelSpaceCorrCluster(dirName, dirSpacing=1000):
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    boxSize = np.array(np.loadtxt(dirName + os.sep + "boxSize.dat"))
    minRad = np.min(np.loadtxt(dirName + os.sep + "particleRad.dat"))
    bins = np.arange(2*minRad, np.sqrt(2)*boxSize[0]/2, 2*minRad)
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    timeList = timeList.astype(int)
    dirList = dirList[np.argwhere(timeList%dirSpacing==0)[:,0]]
    dirList = dirList[-50:]
    #dirList = np.array([dirName])
    velCorrInCluster = np.zeros((bins.shape[0]-1,4))
    countsInCluster = np.zeros(bins.shape[0]-1)
    velCorrOutCluster = np.zeros((bins.shape[0]-1,4))
    countsOutCluster = np.zeros(bins.shape[0]-1)
    for d in range(dirList.shape[0]):
        dirSample = dirName + os.sep + dirList[d]
        if(os.path.exists(dirSample + os.sep + "clusterList.dat")):
            clusterLabel = np.loadtxt(dirSample + os.sep + "clusterList.dat")[:,1]
            #clusterLabel = np.loadtxt(dirSample + os.sep + "deepList.dat")
            #clusterLabel = np.loadtxt(dirSample + os.sep + "noClusterList.dat")
        else:
            clusterLabel = searchClusters(dirSample, numParticles=numParticles)
        #pos = np.array(np.loadtxt(dirName + os.sep + dirList[d] + os.sep + "particlePos.dat"))
        pos = np.array(np.loadtxt(dirSample + os.sep + "particlePos.dat"))
        distance = ucorr.computeDistances(pos, boxSize)
        #vel = np.array(np.loadtxt(dirName + os.sep + dirList[d] + os.sep + "particleVel.dat"))
        vel = np.array(np.loadtxt(dirSample + os.sep + "particleVel.dat"))
        velNorm = np.linalg.norm(vel, axis=1)
        vel[:,0] /= velNorm
        vel[:,1] /= velNorm
        velNormSquared = np.mean(velNorm**2)
        for i in range(distance.shape[0]):
            for j in range(i):
                    for k in range(bins.shape[0]-1):
                        if(distance[i,j] > bins[k] and distance[i,j] <= bins[k+1]):
                            # parallel
                            delta = ucorr.pbcDistance(pos[i], pos[j], boxSize)/distance[i,j]
                            parProj1 = np.dot(vel[i],delta)
                            parProj2 = np.dot(vel[j],delta)
                            # perpendicular
                            deltaPerp = np.array([-delta[1], delta[0]])
                            perpProj1 = np.dot(vel[i],deltaPerp)
                            perpProj2 = np.dot(vel[j],deltaPerp)
                            # correlations
                            if(clusterLabel[i]!=0):
                                velCorrInCluster[k,0] += parProj1 * parProj2
                                velCorrInCluster[k,1] += perpProj1 * perpProj2
                                velCorrInCluster[k,2] += (perpProj1 * parProj2 + parProj1 * perpProj2)*0.5
                                velCorrInCluster[k,3] += np.dot(vel[i],vel[j])
                                countsInCluster[k] += 1
                            else:
                                velCorrOutCluster[k,0] += parProj1 * parProj2
                                velCorrOutCluster[k,1] += perpProj1 * perpProj2
                                velCorrOutCluster[k,2] += (perpProj1 * parProj2 + parProj1 * perpProj2)*0.5
                                velCorrOutCluster[k,3] += np.dot(vel[i],vel[j])
                                countsOutCluster[k] += 1
    binCenter = (bins[1:] + bins[:-1])/2
    for i in range(velCorrInCluster.shape[1]):
        velCorrInCluster[countsOutCluster>0,i] /= countsInCluster[countsOutCluster>0]
        velCorrOutCluster[countsOutCluster>0,i] /= countsOutCluster[countsOutCluster>0]
    #velCorrInCluster /= velNormSquared
    #velCorrOutCluster /= velNormSquared
    np.savetxt(dirName + os.sep + "spaceVelCorrInCluster.dat", np.column_stack((binCenter, velCorrInCluster, countsInCluster)))
    np.savetxt(dirName + os.sep + "spaceVelCorrOutCluster.dat", np.column_stack((binCenter, velCorrOutCluster, countsOutCluster)))
    uplot.plotCorrelation(binCenter, velCorrInCluster[:,0], "$C_{vv}(r)$", "$Distance,$ $r$", color = 'r')
    uplot.plotCorrelation(binCenter, velCorrInCluster[:,1], "$C_{vv}(r)$", "$Distance,$ $r$", color = 'g')
    uplot.plotCorrelation(binCenter, velCorrInCluster[:,2], "$C_{vv}(r)$", "$Distance,$ $r$", color = 'k')
    #plt.show()

def computeClusterPT(dirName, plot=False):
    driving = float(ucorr.readFromDynParams(dirName, "f0"))
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    energy = np.loadtxt(dirName + os.sep + "energy.dat")
    timeStep = ucorr.readFromParams(dirName, "dt")
    numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    if(os.path.exists(dirName + "clusterList.dat")):
        clusterLabel = np.loadtxt(dirName + "clusterList.dat")[:,1]
    else:
        clusterLabel = searchClusters(dirName)
    activePressure = np.zeros((dirList.shape[0], 2))
    temp = np.zeros((dirList.shape[0], 2))
    numParticlesIn = clusterLabel[clusterLabel==1].shape[0]
    numParticlesOut = clusterLabel[clusterLabel!=1].shape[0]
    for i in range(dirList.shape[0]):
        pos = np.loadtxt(dirName + os.sep + dirList[i] + "/particlePos.dat")
        angle = np.loadtxt(dirName + os.sep + dirList[i] + "/particleAngles.dat")
        vel = np.loadtxt(dirName + os.sep + dirList[i] + "/particleVel.dat")
        dir = driving*np.array([np.cos(angle), np.sin(angle)]).T
        activePressure[i,0] = np.sum(np.sum(dir[clusterLabel==1]*pos[clusterLabel==1],axis=1))
        activePressure[i,1] = np.sum(np.sum(dir[clusterLabel!=1]*pos[clusterLabel!=1],axis=1))
        temp[i,0] = np.sum(0.5*np.linalg.norm(vel[clusterLabel==1],axis=0)**2) / numParticlesIn
        temp[i,1] = np.sum(0.5*np.linalg.norm(vel[clusterLabel!=1],axis=0)**2) / numParticlesOut
    print("Active pressure - in: ", np.mean(activePressure[:,0]), " $\\pm$ ", np.std(activePressure[:,0]), " out: ", np.mean(activePressure[:,1]), " $\\pm$ ", np.std(activePressure[:,1]))
    print("Temperature - in: ", np.mean(temp[:,0]), " $\\pm$ ", np.std(temp[:,0]), " out: ", np.mean(temp[:,1]), " $\\pm$ ", np.std(temp[:,1]))
    if(plot=='plot'):
        #uplot.plotCorrelation(timeList, activePressure[:,0], "$Active$ $pressure$ $in$", "$Time,$ $t$")
        #uplot.plotCorrelation(timeList, activePressure[:,1], "$Active$ $pressure$ $out$", "$Time,$ $t$")
        uplot.plotCorrelation(timeList*timeStep, temp[:,0], "$Temperature$ $in$", "$Time,$ $t$")
        uplot.plotCorrelation(timeList*timeStep, temp[:,1], "$Temperature$ $out$", "$Time,$ $t$")
        plt.show()
    return activePressure

######################### Cluster Velocity Correlation #########################
def computeVelocityField(dirName, numBins=100, boxSize=np.array([0,0]), numParticles=None, plot=False, figureName=None, read=False, cluster=False):
    if(numParticles == None):
        numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    if(boxSize[0] == 0):
        boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    bins = np.linspace(-0.5*boxSize[0],0, numBins)
    bins = np.concatenate((np.array([bins[0]-(bins[1]-bins[0])]), bins))
    bins = np.concatenate((bins, np.linspace(0,0.5*boxSize[0],numBins)[1:]))
    if(read=="read" and os.path.exists(dirName + os.sep + "velocityField.dat")):
        grid = np.loadtxt(dirName + os.sep + "velocityGrid.dat")
        field = np.loadtxt(dirName + os.sep + "velocityField.dat")
    else:
        if(cluster=="cluster"):
            print("Computing velocity field for particles in clusters")
            if(os.path.exists(dirName + "clusterList.dat")):
                clusterLabel = np.loadtxt(dirName + "clusterList.dat")[:,1]
            else:
                clusterLabel = searchClusters(dirName, numParticles=numParticles, cluster=cluster)
        elif(cluster=="deep"):
            print("Computing velocity field for particles deep within a cluster")
            if(os.path.exists(dirName + "deepList.dat")):
                clusterLabel = np.loadtxt(dirName + "deepList.dat")
            else:
                clusterLabel = searchClusters(dirName, numParticles=numParticles, cluster=cluster)
        elif(cluster=="nocluster"):
            print("Computing velocity field for particles not in a cluster")
            if(os.path.exists(dirName + "noClusterList.dat")):
                clusterLabel = np.loadtxt(dirName + "noClusterList.dat")
            else:
                clusterLabel = searchClusters(dirName, numParticles=numParticles, cluster=cluster)
        else:
            print("Computing velocity field for all particles")
            clusterLabel = np.ones(numParticles)
        vel = np.array(np.loadtxt(dirName + os.sep + "particleVel.dat"))
        pos = np.array(np.loadtxt(dirName + os.sep + "particlePos.dat"))
        delta = ucorr.computeDeltas(pos, boxSize)
        bins = np.linspace(-0.5*boxSize[0],0, numBins)
        bins = np.concatenate((np.array([bins[0]-(bins[1]-bins[0])]), bins))
        bins = np.concatenate((bins, np.linspace(0,0.5*boxSize[0],numBins)[1:]))
        numBins = bins.shape[0]
        field = np.zeros((numBins, numBins, 2))
        grid = np.zeros((numBins, numBins, 2))
        for k in range(numBins-1):
            for l in range(numBins-1):
                grid[k,l,0] = bins[k]
                grid[k,l,1] = bins[l]
        for i in range(numParticles):
            if(clusterLabel[i]!=0):
                rotation = np.array([[vel[i,0], -vel[i,1]], [vel[i,1], vel[i,0]]]) / np.linalg.norm(vel[i])
                for j in range(numParticles):
                    for k in range(numBins-1):
                        if(delta[i,j,0] > bins[k] and delta[i,j,0] <= bins[k+1]):
                            for l in range(numBins-1):
                                if(delta[i,j,1] > bins[l] and delta[i,j,1] <= bins[l+1]):
                                    field[k,l] += np.matmul(rotation, vel[j])
        field = field.reshape(numBins*numBins, 2)
        field /= np.max(np.linalg.norm(field,axis=1))
        grid = grid.reshape(numBins*numBins, 2)
        if(cluster=="cluster"):
            np.savetxt(dirName + os.sep + "velocityGridInCluster.dat", grid)
            np.savetxt(dirName + os.sep + "velocityFieldInCluster.dat", field)
        else:
            np.savetxt(dirName + os.sep + "velocityGrid.dat", grid)
            np.savetxt(dirName + os.sep + "velocityField.dat", field)
    if(plot=="plot"):
        xBounds = np.array([bins[0], bins[-1]])
        yBounds = np.array([bins[0], bins[-1]])
        fig = plt.figure(0, dpi = 150)
        ax = fig.gca()
        ax.set_xlim(xBounds[0], xBounds[1])
        ax.set_ylim(yBounds[0], yBounds[1])
        ax.set_aspect('equal', adjustable='box')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.quiver(grid[:,0], grid[:,1], field[:,0], field[:,1], facecolor='k', width=0.004, headlength=3, headaxislength=3)
        plt.savefig("/home/francesco/Pictures/soft/packings/vfield-" + figureName + ".png", transparent=False, format = "png")
        plt.show()
    return grid, field

######################### Cluster Velocity Correlation #########################
def averageVelocityField(dirName, dirSpacing=1000, numBins=100, boxSize=np.array([0,0]), numParticles=None, plot=False, figureName=None, cluster=False):
    dirList, timeList = ucorr.getOrderedDirectories(dirName)
    timeList = timeList.astype(int)
    dirList = dirList[np.argwhere(timeList%dirSpacing==0)[:,0]]
    dirList = dirList[-10:]
    if(numParticles == None):
        numParticles = int(ucorr.readFromParams(dirName, "numParticles"))
    if(boxSize[0] == 0):
        boxSize = np.loadtxt(dirName + os.sep + "boxSize.dat")
    bins = np.linspace(-0.5*boxSize[0],0, numBins)
    bins = np.concatenate((np.array([bins[0]-(bins[1]-bins[0])]), bins))
    bins = np.concatenate((bins, np.linspace(0,0.5*boxSize[0],numBins)[1:]))
    numBins = bins.shape[0]
    field = np.zeros((numBins*numBins, 2))
    grid = np.zeros((numBins*numBins, 2))
    for d in range(dirList.shape[0]):
        dirSample = dirName + os.sep + dirList[d]
        gridTemp, fieldTemp = computeVelocityField(dirSample, numBins, cluster=cluster)
        grid += gridTemp
        field += fieldTemp
    grid /= dirList.shape[0]
    field /= dirList.shape[0]
    if(cluster=="cluster"):
        np.savetxt(dirName + os.sep + "averageVelocityGridInCluster.dat", grid)
        np.savetxt(dirName + os.sep + "averageVelocityFieldInCluster.dat", field)
    if(cluster=="deep"):
        np.savetxt(dirName + os.sep + "averageVelocityGridDeepCluster.dat", grid)
        np.savetxt(dirName + os.sep + "averageVelocityFieldDeepCluster.dat", field)
    if(cluster=="nocluster"):
        np.savetxt(dirName + os.sep + "averageVelocityGridNoCluster.dat", grid)
        np.savetxt(dirName + os.sep + "averageVelocityFieldNoCluster.dat", field)
    else:
        np.savetxt(dirName + os.sep + "averageVelocityGrid.dat", grid)
        np.savetxt(dirName + os.sep + "averageVelocityField.dat", field)
    if(plot=="plot"):
        xBounds = np.array([bins[0], bins[-1]])
        yBounds = np.array([bins[0], bins[-1]])
        fig = plt.figure(0, dpi = 150)
        ax = fig.gca()
        ax.set_xlim(xBounds[0], xBounds[1])
        ax.set_ylim(yBounds[0], yBounds[1])
        ax.set_aspect('equal', adjustable='box')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.quiver(grid[:,0], grid[:,1], field[:,0], field[:,1], facecolor='k', width=0.004, headlength=3, headaxislength=3)
        plt.savefig("/home/francesco/Pictures/soft/packings/avfield-" + figureName + ".png", transparent=False, format = "png")
        plt.show()
    return grid, field

if __name__ == '__main__':
    dirName = sys.argv[1]
    whichCorr = sys.argv[2]

    if(whichCorr == "paircorr"):
        plot = sys.argv[3]
        computePairCorr(dirName, plot)

    elif(whichCorr == "sus"):
        sampleName = sys.argv[3]
        maxPower = int(sys.argv[4])
        computeParticleSusceptibility(dirName, sampleName, maxPower)

    elif(whichCorr == "lincorrx"):
        maxPower = int(sys.argv[3])
        computeParticleSelfCorrOneDim(dirName, maxPower)

    elif(whichCorr == "logcorrx"):
        startBlock = int(sys.argv[3])
        maxPower = int(sys.argv[4])
        freqPower = int(sys.argv[5])
        computeParticleLogSelfCorrOneDim(dirName, startBlock, maxPower, freqPower)

    elif(whichCorr == "lincorr"):
        maxPower = int(sys.argv[3])
        computeParticleSelfCorr(dirName, maxPower)

    elif(whichCorr == "checkcorr"):
        initialBlock = int(sys.argv[3])
        numBlocks = int(sys.argv[4])
        maxPower = int(sys.argv[5])
        plot = sys.argv[6]
        computeTau = sys.argv[7]
        checkParticleSelfCorr(dirName, initialBlock, numBlocks, maxPower, plot=plot, computeTau=computeTau)

    elif(whichCorr == "collecttemp"):
        collectRelaxationDataVSTemp(dirName)

    elif(whichCorr == "logcorr"):
        startBlock = int(sys.argv[3])
        maxPower = int(sys.argv[4])
        freqPower = int(sys.argv[5])
        qFrac = sys.argv[6]
        computeTau = sys.argv[7]
        computeParticleLogSelfCorr(dirName, startBlock, maxPower, freqPower, qFrac, computeTau=computeTau)

    elif(whichCorr == "corrsingle"):
        startBlock = int(sys.argv[3])
        maxPower = int(sys.argv[4])
        freqPower = int(sys.argv[5])
        qFrac = sys.argv[6]
        computeSingleParticleLogSelfCorr(dirName, startBlock, maxPower, freqPower, qFrac)

    elif(whichCorr == "collectphi"):
        dynName = sys.argv[3]
        collectRelaxationDataVSPhi(dirName, dynName)

    elif(whichCorr == "temppdf"):
        numBins = int(sys.argv[3])
        plot = sys.argv[4]
        computeLocalTemperaturePDF(dirName, numBins, plot)

    elif(whichCorr == "collecttemppdf"):
        numBins = int(sys.argv[3])
        plot = sys.argv[4]
        collectLocalTemperaturePDF(dirName, numBins, plot)

    elif(whichCorr == "velpdf"):
        computeParticleVelPDF(dirName)

    elif(whichCorr == "velsubset"):
        firstIndex = int(sys.argv[3])
        mass = float(sys.argv[4])
        computeParticleVelPDFSubSet(dirName, firstIndex, mass)

    elif(whichCorr == "velcorr"):
        computeParticleVelTimeCorr(dirName)

    elif(whichCorr == "blockvelcorr"):
        numBlocks = int(sys.argv[3])
        computeParticleBlockVelTimeCorr(dirName, numBlocks)

    elif(whichCorr == "logvelcorr"):
        startBlock = int(sys.argv[3])
        maxPower = int(sys.argv[4])
        freqPower = int(sys.argv[5])
        computeParticleLogVelTimeCorr(dirName, startBlock, maxPower, freqPower)

    elif(whichCorr == "velspacecorr"):
        computeParticleVelSpaceCorr(dirName)

    elif(whichCorr == "averagevc"):
        averageParticleVelSpaceCorr(dirName)

    elif(whichCorr == "averagevccluster"):
        averageParticleVelSpaceCorrCluster(dirName)

    elif(whichCorr == "averagepc"):
        dirSpacing = int(sys.argv[3])
        averagePairCorr(dirName, dirSpacing)

    elif(whichCorr == "collision"):
        check = sys.argv[3]
        numBins = int(sys.argv[4])
        getCollisionIntervalPDF(dirName, check, numBins)

    elif(whichCorr == "contact"):
        check = sys.argv[3]
        spacing = int(sys.argv[4])
        getContactCollisionIntervalPDF(dirName, check, spacing)

    elif(whichCorr == "activep"):
        computeActivePressure(dirName)

    elif(whichCorr == "density"):
        numBins = int(sys.argv[3])
        plot = sys.argv[4]
        computeLocalDensity(dirName, numBins, plot)

    elif(whichCorr == "densitytime"):
        numBins = int(sys.argv[3])
        plot = sys.argv[4]
        localDensityVSTime(dirName, numBins, plot)

    elif(whichCorr == "averageld"):
        numBins = int(sys.argv[3])
        averageLocalDensity(dirName, numBins)

    elif(whichCorr == "cluster"):
        numParticles = int(sys.argv[3])
        plot = sys.argv[4]
        cluster = sys.argv[5]
        searchClusters(dirName, numParticles, plot=plot, cluster=cluster)

    elif(whichCorr == "clusterpt"):
        plot = sys.argv[3]
        computeClusterPT(dirName, plot=plot)

    elif(whichCorr == "vfield"):
        numBins = int(sys.argv[3])
        plot = sys.argv[4]
        figureName = sys.argv[5]
        cluster = sys.argv[6]
        computeVelocityField(dirName, numBins=numBins, plot=plot, figureName=figureName, cluster=cluster)

    elif(whichCorr == "averagevfield"):
        numBins = int(sys.argv[3])
        plot = sys.argv[4]
        figureName = sys.argv[5]
        cluster = sys.argv[6]
        computeVelocityField(dirName, numBins=numBins, plot=plot, figureName=figureName, cluster=cluster)

    else:
        print("Please specify the correlation you want to compute")
