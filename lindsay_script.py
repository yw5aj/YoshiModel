import os
os.chdir('x:/WorkFolder/AbaqusFolder/YoshiModel/')


import numpy as np
from abqimport import *
from setfiber import *
from feconstants import materialBlockFiber as materialBlock


# %% For Yoshi's experiment
stimBlock = getStimBlockFromCsv('x:/WorkFolder/DataAnalysis/YoshiRecordingData/csvs/stim_block_2.csv')
# The fast one
fiber = Fiber(baseModelName='LindsayFiberFast', suffix='', stimBlock=stimBlock, materialBlock=materialBlock, runFiber=True, doAnalysis=False, skipWait=True)
np.savetxt('./csvs/'+fiber.baseModelName+'StaticForceDispl.csv', np.column_stack((fiber.staticDisplList, fiber.staticForceList)), delimiter=',')
for i, model in enumerate(fiber.modelList):
    output = np.c_[model.time, model.force, model.displ, model.stress, model.strain, model.sener]
    np.savetxt('./csvs/'+fiber.baseModelName+'Output'+str(i)+'.csv', output, delimiter=',')
# The slow one
stimBlock['rampLiftTimeArray'] *= 4
fiber = Fiber(baseModelName='LindsayFiberSlow', suffix='', stimBlock=stimBlock, materialBlock=materialBlock, runFiber=True, doAnalysis=False, skipWait=True)
np.savetxt('./csvs/'+fiber.baseModelName+'StaticForceDispl.csv', np.column_stack((fiber.staticDisplList, fiber.staticForceList)), delimiter=',')
for i, model in enumerate(fiber.modelList):
    output = np.c_[model.time, model.force, model.displ, model.stress, model.strain, model.sener]
    np.savetxt('./csvs/'+fiber.baseModelName+'Output'+str(i)+'.csv', output, delimiter=',')


# %% For the simulations
def runSimulation(baseModelName, materialBlock):
    # Run displacement controlled analysis
    fiber = Fiber(baseModelName=baseModelName, materialBlock=materialBlock, runFiber=True, doAnalysis=True, skipWait=True)
    # Now to force controlled
    fiberForce = FiberForce(fiber, runFiber=True, doAnalysis=True, skipWait=True)
    return

runSimulation('Lindsay', materialBlock)

from readodb import getSurfaceDistribution
for fname in os.listdir('./odbs'):
    if fname.endswith('.odb') and fname.startswith('Lindsay'):
        getSurfaceDistribution(fname[:-4])

