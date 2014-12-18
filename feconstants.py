import numpy as np
import copy
# Set default stim block for displ
_displtimecoeff = np.loadtxt('./csvs/displtimecoeff.csv', delimiter=',')
stimBlockDefault = {'holdDisplArray': np.r_[.032:.16:5j]}
stimBlockDefault['rampLiftTimeArray'] = np.polyval(_displtimecoeff, stimBlockDefault['holdDisplArray'])
# Set default stim block for force
stimBlockDefaultForce = {'holdForceArray': np.r_[1.2e-3:6e-3:5j]}
_displforce = np.loadtxt('./csvs/FitFemDisplforce.csv', delimiter=',')
eqdisp = np.interp(stimBlockDefaultForce['holdForceArray'], _displforce[:, 1], _displforce[:, 0]*1e3)
stimBlockDefaultForce['rampLiftTimeArray'] = np.polyval(_displtimecoeff, eqdisp)
# Set stim line and material
stimLineDefault = {'rampLiftTime': .4, 'holdDispl': .2*1e-3}
materialBlockDefault = {'thicknessAll': [418.5, 338.8, 10.1348], 'skin_g_array': [0.351, 0.154, 0.495], 
    'skin_tau_array': [np.inf, 1.111, .092], 'skin_mu': 6.354e3, 'skin_alpha': 8.787,
    'sylgard_c10': 1.05e5, 'sylgard_g': 0.03, 'sylgard_tau': 0.7}
# Try a new skin to fit the transduction function
skinThickArray, skinAlphaArray, sylgardThickArray, sylgardC10Array, g1Array, g2Array, ginfArray = np.genfromtxt('./csvs/simprop.csv', delimiter=',').T
materialBlockFiber = copy.deepcopy(materialBlockDefault)
materialBlockFiber['thicknessAll'][0] = skinThickArray[0]