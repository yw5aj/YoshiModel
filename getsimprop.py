# -*- coding: utf-8 -*-
"""
Created on Sun May  4 20:46:55 2014

@author: Yuxiang Wang
"""

import numpy as np, pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt

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
    real_ginf_min = simprop['ginf'][0]
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
    #%% Save dataframe to excel
    pd.DataFrame(simprop).to_excel('./csvs/simprop.xlsx')
    #%% Plot out as boxplots
    fig, axs = plt.subplots()
    bp_labels = [r'Thickness ($\mu$m)', 'Modulus', 'Viscoelasticity']
    bp_array = np.c_[thickness, alpha, ginf]
    bp = axs.boxplot(bp_array/bp_array.mean(axis=0), labels=bp_labels)
    bp_feature_array = np.c_[simprop_array[:, 0], simprop_array[:, 1],
                            simprop_array[:, 6]]
    bp_feature_array[0, 2] = real_ginf_min
#    for line in bp.values():
#        plt.setp(line, color='k')
    axs.set_yticks([])
    axs.set_ylim(bottom=-.1)
    for i in range(len(bp_labels)):
        for val in bp_feature_array[:, i]:
            text = '%d' % val if i == 0 else '%.2f' % val
            axs.annotate(text, color='.0', va='center',
                          xy=(i+1, val/bp_array[:, i].mean()),
                          xytext=(i+1.18, val/bp_array[:, i].mean()))
    # Save figure
    fig.tight_layout()
    fig.savefig('./figures/boxplot_prop.png', dpi=300)
    plt.close(fig)
    # %% Design data for the relax adapt analysis
    p_ginf = np.polyfit(thickness, ginf, 1)
    p_g1 = np.polyfit(thickness, g1, 1)
    rathick_ginf = np.polyval(p_ginf, simprop['thickness'])
    rathick_g1 = np.polyval(p_g1, simprop['thickness'])
    rathick_g2 = 1 - rathick_ginf - rathick_g1
    np.savetxt('./csvs/rathickg.csv', np.c_[
        rathick_g1, rathick_g2, rathick_ginf], delimiter=',')
