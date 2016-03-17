import os
os.chdir('x:/YuxiangWang/AbaqusFolder/YoshiModel/')

from setfiber import *

repsampleArr = np.genfromtxt('./csvs/repsample.csv', delimiter=',')
runFiber = False
writeInput = True

# Don't change
runForce = False
doAnalysis = False
skipWait = True

stimBlock = setHoldDisplArray(np.r_[.1:.6:6j])
stimBlockForce = setHoldForceArray(np.r_[1.3e-3:7.8e-3:6j])

def runSimulation(baseModelName, materialBlock):
    # Run displacement controlled analysis
    fiber = Fiber(baseModelName=baseModelName, materialBlock=materialBlock,
                  stimBlock=stimBlock,
                  runFiber=runFiber, doAnalysis=doAnalysis, skipWait=skipWait,
                  writeInput=writeInput)
    # Now to force controlled
    # Note: need to refactor the code to tune force levels yet 
    # if cylinder radius is not 0.5
    if runForce:
        fiberForce = FiberForce(fiber, runFiber=runFiber, doAnalysis=doAnalysis,
                                stimBlock=stimBlockForce, skipWait=skipWait,
                                writeInput=writeInput)
    return


for sample_id, (tau1, tau2, g1, g2, ginf, mu, alpha, thickness) in enumerate(
        repsampleArr):
    if sample_id == 0:  # Only run the typical skin
        materialBlock = copy.deepcopy(materialBlockDefault)
        materialBlock['skin_tau_array'] = [np.inf, tau2, tau1]
        materialBlock['skin_g_array'] = [ginf, g2, g1]
        materialBlock['skin_mu'] = mu * alpha / 2
        materialBlock['skin_alpha'] = alpha
        materialBlock['thicknessAll'][0] = thickness
        materialBlock['cylinderRadius'] = .75
        runSimulation('TipOneFive%d' % sample_id, materialBlock)


# Get distribution csvs
from readodb import getSurfaceDistribution
for fname in os.listdir('./odbs'):
    if fname.endswith('.odb') and fname.startswith('TipOneFive'):
        getSurfaceDistribution(fname[:-4])

