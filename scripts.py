import os
os.chdir('x:/WorkFolder/AbaqusFolder/YoshiModel/')

from abqimport import *
from setfiber import *
import copy

skinThickArray, skinAlphaArray, sylgardThickArray, sylgardC10Array, g1Array, g2Array, ginfArray = np.genfromtxt('./csvs/simprop.csv', delimiter=',').T
runFiber = True
doAnalysis = True
skipWait = True

def runSimulation(baseModelName, materialBlock):
    # Run displacement controlled analysis
    fiber = Fiber(baseModelName=baseModelName, materialBlock=materialBlock, runFiber=runFiber,
        doAnalysis=doAnalysis, skipWait=skipWait)
    # Now to force controlled
    fiberForce = FiberForce(fiber, runFiber=runFiber, doAnalysis=doAnalysis, skipWait=skipWait)
    return


# Vary skin thickness
for (level, skinThick) in enumerate(skinThickArray):
    # Assign material properties
    materialBlock = copy.deepcopy(materialBlockDefault)
    materialBlock['thicknessAll'][0] = skinThick
    runSimulation('SkinThick%d'%level, materialBlock)


# Vary skin alpha
for (level, skinAlpha) in enumerate(skinAlphaArray):
    # Assign material properties
    materialBlock = copy.deepcopy(materialBlockDefault)
    materialBlock['skin_alpha'] = skinAlpha
    runSimulation('SkinAlpha%d'%level, materialBlock)

# Vary sylgard thickness
for (level, sylgardThick) in enumerate(sylgardThickArray):
    # if level < 4:
        # continue
    # Assign material properties
    materialBlock = copy.deepcopy(materialBlockDefault)
    materialBlock['thicknessAll'][2] = sylgardThick
    runSimulation('SylgardThick%d'%level, materialBlock)


# Vary sylgard c10
for (level, sylgardC10) in enumerate(sylgardC10Array):
    # Assign material properties
    materialBlock = copy.deepcopy(materialBlockDefault)
    materialBlock['sylgard_c10'] = sylgardC10
    runSimulation('SylgardC10%d'%level, materialBlock)


# Vary skin viscoelasticity
for (level, ginf) in enumerate(ginfArray):
    # Get g1, g2, ginf
    g1 = g1Array[level]
    g2 = g2Array[level]
    # Assign material properties
    materialBlock = copy.deepcopy(materialBlockDefault)
    materialBlock['skin_g_array'] = [ginf, g2, g1]
    runSimulation('SkinGinf%d'%level, materialBlock)


# Get distribution csvs
from readodb import getSurfaceDistribution
for fname in os.listdir('./odbs'):
    if fname.endswith('.odb') and fname.startswith('S'):
        getSurfaceDistribution(fname[:-4])