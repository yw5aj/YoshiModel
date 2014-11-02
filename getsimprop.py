# -*- coding: utf-8 -*-
"""
Created on Sun May  4 20:46:55 2014

@author: Yuxiang Wang
"""

import numpy as np, pandas as pd
from scipy.io import loadmat

def get_simprop(data):
    median = np.median(data)
    upper_quartile = np.percentile(data, 75)
    lower_quartile = np.percentile(data, 25)
    iqr = upper_quartile - lower_quartile
    upper_whisker = data[data<=upper_quartile+1.5*iqr].max()
    lower_whisker = data[data>=lower_quartile-1.5*iqr].min()
    simprop = np.array([lower_whisker, lower_quartile, median, upper_quartile,
                        upper_whisker])
    return simprop


if __name__ == '__main__':
    # Load data from viscoelasticity dataset
    data = loadmat(
        'X:/WorkFolder/DataAnalysis/skinMechanicsAll/analysis/ViscoAnalysis052013/strain_level_2py.mat')
    tau1, tau2, g1, g2, ginf, mu, alpha, r2, stretch, thickness, skin_id,\
        ramp_time = data['qlv2tFixPara'].T
    thickness *= 1e3
    # Creat the thicknesses and the alphas
    simprop = {}
    prop_list = ['thickness', 'alpha', 'ginf']
    for prop in prop_list:
        simprop[prop] = get_simprop(globals()[prop])
    # Manually adjust ginf and g1, g2
    simprop['ginf'][0] = .15
    p = np.polyfit(ginf, g1, 1)
    simprop['g1'] = np.polyval(p, simprop['ginf'])
    simprop['g2'] = 1. - simprop['g1'] - simprop['ginf']
    # Add sylgard elasticity and thickness
    sylgardh = 10.1348
    sylgarde = 1.05e5
    simprop['sylgardh'] = sylgardh * np.r_[.5:1.5:5j]
    simprop['sylgarde'] = sylgarde * np.r_[.5:1.5:5j]
    simprop_array = np.c_[simprop['thickness'], simprop['alpha'],
                          simprop['sylgardh'], simprop['sylgarde'],
                          simprop['g1'], simprop['g2'], simprop['ginf'],
                         ]
    np.savetxt('./csvs/simprop.csv', simprop_array, delimiter=',')
    # Save dataframe to excel
    pd.DataFrame(simprop).to_excel('./csvs/simprop.xlsx')
