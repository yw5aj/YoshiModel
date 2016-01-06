# -*- coding: utf-8 -*-
"""
Created on Sun May  4 20:46:55 2014

@author: Yuxiang Wang
"""

import numpy as np
import pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt


def get_simprop(data):
    median = np.median(data)
    upper_quartile = np.percentile(data, 75)
    lower_quartile = np.percentile(data, 25)
    iqr = upper_quartile - lower_quartile
    upper_whisker = data[data <= upper_quartile+1.5*iqr].max()
    lower_whisker = data[data >= lower_quartile-1.5*iqr].min()
    simprop = np.array([lower_whisker, lower_quartile, median, upper_quartile,
                        upper_whisker])
    return simprop


if __name__ == '__main__':
    # Load data from viscoelasticity dataset
    data = loadmat(
        'X:/WorkFolder/DataAnalysis/skinMechanicsAll/analysis/' +
        'ViscoAnalysis052013/strain_level_2py.mat')
    tau1, tau2, g1, g2, ginf, mu, alpha, r2, stretch, thickness, skin_id,\
        ramp_time = data['qlv2tFixPara'].T
    skin_id = skin_id.astype('i')
    thickness *= 1e3
    # Creat the thicknesses and the alphas
    simprop = {}
    prop_list = ['thickness', 'alpha', 'ginf']
    for prop in prop_list:
        simprop[prop] = get_simprop(globals()[prop])
    # Manually adjust ginf and g1, g2
    real_ginf_min = simprop['ginf'][0]
    simprop['ginf'][0] = .1
    p = np.polyfit(ginf, g1, 1)
    # Calculate p-value for this regression
    from scipy.stats import linregress
    res = linregress(ginf, g1)
    # Done for the p-value
    simprop['g1'] = np.polyval(p, simprop['ginf'])
    simprop['g2'] = 1. - simprop['g1'] - simprop['ginf']
    # Add sylgard elasticity and thickness
    sylgardh = 10.1348
    sylgarde = 1.05e5
    simprop['sylgardh'] = sylgardh * np.r_[.5:1.5:5j]
    simprop['sylgarde'] = sylgarde * np.r_[.5:1.5:5j]
    simprop_array = np.c_[simprop['thickness'], simprop['alpha'],
                          simprop['sylgardh'], simprop['sylgarde'],
                          simprop['g1'], simprop['g2'], simprop['ginf']]
    np.savetxt('./csvs/simprop.csv', simprop_array, delimiter=',')
    # %% Save dataframe to excel
    pd.DataFrame(simprop).to_excel('./csvs/simprop.xlsx')
    # %% Plot out as boxplots
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
    # For the thickness induced changes
    p_ginf = np.polyfit(thickness, ginf, 1)
    p_g1 = np.polyfit(thickness, g1, 1)
    rathick_ginf = np.polyval(p_ginf, simprop['thickness'])
    rathick_g1 = np.polyval(p_g1, simprop['thickness'])
    rathick_g2 = 1 - rathick_ginf - rathick_g1
    np.savetxt('./csvs/rathickg.csv', np.c_[
        rathick_g1, rathick_g2, rathick_ginf], delimiter=',')
    # For the individual differences
    residuals = ginf - np.polyval(p_ginf, thickness)
    ginf_residuals = get_simprop(residuals)
    raind_ginf = np.median(ginf) + ginf_residuals
    p_ginf_to_g1 = np.polyfit(ginf, g1, 1)
    raind_g1 = np.polyval(p_ginf_to_g1, raind_ginf)
    raind_g2 = 1 - raind_ginf - raind_g1
    np.savetxt('./csvs/raindg.csv', np.c_[
        raind_g1, raind_g2, raind_ginf], delimiter=',')
    # %% A step-wise way to draw samples
    dataset = '2013'
    if dataset == '2013':
        population_data = np.c_[tau1, tau2, g1, g2, ginf, mu, alpha, thickness]
        skin_id_arr = np.unique(skin_id)
        unique_skin_ind = []
        for i in skin_id_arr:
            unique_skin_ind.append(
                np.median(np.nonzero(skin_id == i)[0]).astype('i'))
        population_data = population_data[unique_skin_ind, :]
    elif dataset == '2011':
        xlsx_df = pd.read_excel(
            'X:/WorkFolder/WorkArchive/DocumentFolder201507/分析/201404/' +
            'ViscoAnalysis0411.xlsm', sheetname='SummerFast',
            index_col=None, header=None)
        qlv_params = xlsx_df.iloc[5:49, 25:32].values.astype('f')
        thickness = xlsx_df.iloc[5:49, 10].values.astype('f')
        age = xlsx_df.iloc[5:49, 5]
        population_data = np.c_[qlv_params, thickness]
    from sklearn.preprocessing import scale
    norm_population_data = scale(population_data)
    sample_ind = np.array([])

    def add_sample(norm_population_data, old_sample_ind):
        if len(old_sample_ind) == 0:
            new_sample_ind = np.array([((
                norm_population_data - norm_population_data.mean(
                    axis=0))**2).sum(axis=1).argmin()])
            return new_sample_ind
        else:
            covres_array = np.zeros((norm_population_data.shape[0]))
            for new_ind in range(norm_population_data.shape[0]):
                if new_ind in old_sample_ind:
                    covres_array[new_ind] = np.inf
                else:
                    new_sample_ind = np.r_[old_sample_ind, new_ind]
                    covres_array[new_ind] = calculate_covres(
                        norm_population_data, new_sample_ind)
            new_ind = covres_array.argmin()
            new_sample_ind = np.r_[old_sample_ind, new_ind]
            return new_sample_ind

    def calculate_covres(population_data, sample_ind):
        sample_data = population_data[sample_ind, :]
        population_cov = np.cov(population_data, rowvar=0)
        sample_cov = np.cov(sample_data, rowvar=0)
        covres = ((population_cov - sample_cov)**2).sum()
        return covres
    # Make the convergence plot
    covtot = (np.cov(norm_population_data, rowvar=0)**2).sum()
    covres_list = [covtot]
    for i in range(41):
        sample_ind = add_sample(norm_population_data, sample_ind)
        covres_list.append(calculate_covres(norm_population_data, sample_ind))
    rel_err = np.array(covres_list) / covtot
    fig, axs = plt.subplots()
    axs.plot(100 * (1 - rel_err), '-k')
    axs.set_title('Population N = 41')
    axs.set_xlabel('# of samples')
    axs.set_ylabel('% of covariance matrix')
    axs.grid()
    fig.tight_layout()
    fig.savefig('./figures/cov_converge.png', dpi=300)
    # Get actual data
    sample_data = population_data[sample_ind[:10], :]
    np.savetxt('./csvs/repsample.csv', sample_data, delimiter=',')
