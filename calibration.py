import os
os.chdir('X:/WorkFolder/AbaqusFolder/YoshiModel')
from abqimport import *


def getFitFem(runFiber=True, doAnalysis=True):
    from constants import materialBlockFiber as materialBlock
    stimBlock = {'rampLiftTimeArray': .4*np.ones(10), 'holdDisplArray': np.r_[25:250:10j]*1e-3}
    from setfiber import Fiber
    fiber = Fiber(baseModelName='FitFem', suffix='', stimBlock=stimBlock, materialBlock=materialBlock, runFiber=runFiber, doAnalysis=doAnalysis, skipWait=False)
    if doAnalysis or runFiber:
        np.savetxt('./csvs/FitFemDisplForce.csv', np.column_stack((fiber.staticDisplList, fiber.staticForceList)), delimiter=',')
    return

getFitFem()

import sys
sys.exit()