import os
os.chdir('x:/WorkFolder/AbaqusFolder/YoshiModel/')

from abqimport import *
from setfiber import *
import copy

repsampleArr = np.genfromtxt('./csvs/repsample.csv', delimiter=',')
runFiber = True
runForce = False
doAnalysis = True
skipWait = True

def runSimulation(baseModelName, materialBlock):
    # Run displacement controlled analysis
    fiber = Fiber(baseModelName=baseModelName, materialBlock=materialBlock,
                  runFiber=runFiber, doAnalysis=doAnalysis, skipWait=skipWait)
    # Now to force controlled
    # Note: need to refactor the code to tune force levels yet
    if runForce:
        fiberForce = FiberForce(fiber, runFiber=runFiber, doAnalysis=doAnalysis,
                                skipWait=skipWait)
    return


for sample_id, (tau1, tau2, g1, g2, ginf, mu, alpha, thickness) in enumerate(
        repsampleArr):
    print(sample_id)
    print(tau1, tau2)
    materialBlock = copy.deepcopy(materialBlockDefault)
    materialBlock['skin_tau_array'] = [np.inf, tau2, tau1]
    materialBlock['skin_g_array'] = [ginf, g2, g1]
    materialBlock['skin_mu'] = mu * alpha / 2
    materialBlock['skin_alpha'] = alpha
    materialBlock['thicknessAll'][0] = thickness
    materialBlock['cylinderRadius'] = .75
    runSimulation('RepSample%d' % sample_id, materialBlock)




# Get distribution csvs
# from readodb import getSurfaceDistribution
# for fname in os.listdir('./odbs'):
#     if fname.endswith('.odb') and fname.startswith('S'):
#         getSurfaceDistribution(fname[:-4])
