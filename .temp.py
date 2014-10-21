from abqimport import *

materialBlock = {'thicknessAll': (418.5, 338.8, 10.1348), 'skin_g_array': (0.351, 0.110, 0.482), 
    'skin_tau_array': (np.inf, 1.111, .092), 'skin_mu': 6.354e3, 'skin_alpha': 8.787,
    'sylgard_c10': 1.05e5, 'sylgard_g': 0.03, 'sylgard_tau': 0.7}

stimBlock = {'rampLiftTimeArray': .4*np.ones(10), 'holdDisplArray': np.r_[25:250:10j]*1e-3}

from setfiber import Fiber

fiber = Fiber(baseModelName='FitFem', stimBlock=stimBlock, materialBlock=materialBlock, runFiber=True, doAnalysis=False, skipWait=False)
np.savetxt('./csvs/FitFemDisplForce.csv', np.column_stack((fiber.staticDisplList, fiber.staticForceList)), delimiter=',')

