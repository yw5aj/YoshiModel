import os
os.chdir('x:/YuxiangWang/AbaqusFolder/YoshiModel/')

from abqimport import *
from setfiber import *
import copy

runFiberDispl = True
doAnalysisDispl = True
runFiberForce = True
doAnalysisForce = True
skipWait = True

def runSimulation(baseModelName, materialBlock, stimBlockForce):
    # Run displacement controlled analysis
    fiber = Fiber(baseModelName=baseModelName, materialBlock=materialBlock, runFiber=runFiberDispl,
        doAnalysis=doAnalysisDispl, skipWait=skipWait)
    # Now to force controlled
    fiberForce = FiberForce(fiber, stimBlock=stimBlockForce, runFiber=runFiberForce, doAnalysis=doAnalysisForce, skipWait=skipWait)
    return


# Set force array
_displtimecoeff = np.loadtxt('./csvs/displtimecoeff.csv', delimiter=',')
stimBlockForce = {'holdForceArray': np.r_[1.5e-3:7.5e-3:5j]}
_displforce = np.loadtxt('./csvs/FitFemDisplforce.csv', delimiter=',')
eqdisp = np.interp(stimBlockDefaultForce['holdForceArray'], _displforce[:, 1], _displforce[:, 0]*1e3)
stimBlockForce['rampLiftTimeArray'] = np.polyval(_displtimecoeff, eqdisp)

    
# Simulations for the homeostasis analysis
hmstssArray = np.linspace(125, 433, 10)
for (level, skinThick) in enumerate(hmstssArray):
    # Assign material properties
    materialBlock = copy.deepcopy(materialBlockDefault)
    materialBlock['thicknessAll'][0] = skinThick
    runSimulation('Hmstss%d'%level, materialBlock, stimBlockForce)


# Get distribution csvs
from readodb import getSurfaceDistribution
for fname in os.listdir('./odbs'):
    if fname.endswith('.odb') and fname.startswith('Hmstss'):
        getSurfaceDistribution(fname[:-4])

