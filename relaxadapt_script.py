import os
os.chdir('x:/WorkFolder/AbaqusFolder/YoshiModel/')

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

    
skinThickArray, skinAlphaArray, sylgardThickArray, sylgardC10Array, g1Array, g2Array, ginfArray = np.genfromtxt(
    './csvs/simprop.csv', delimiter=',').T
raThickG1Array, raThickG2Array, raThickGinfArray = np.genfromtxt('./csvs/rathickg.csv', delimiter=',').T


# Simulations for the homeostasis analysis
raThickArray = skinThickArray
for level, (raThick, raThickG1, raThickG2, raThickGinf) in enumerate(zip(raThickArray, raThickG1Array, raThickG2Array, raThickGinfArray)):
    # Assign material properties
    materialBlock = copy.deepcopy(materialBlockDefault)
    materialBlock['thicknessAll'][0] = raThick
    materialBlock['skin_g_array'] = [raThickGinf, raThickG2, raThickG1]
    runSimulation('RaThick%d'%level, materialBlock, stimBlockForce)


# Get distribution csvs
from readodb import getSurfaceDistribution
for fname in os.listdir('./odbs'):
    if fname.endswith('.odb') and fname.startswith('Ra'):
        getSurfaceDistribution(fname[:-4])

