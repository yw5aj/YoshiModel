# -*- coding: utf-8 -*-
"""
Created on Sun May  4 20:46:55 2014

@author: Yuxiang Wang
"""

import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.stats import linregress
from sklearn.preprocessing import scale
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


def load_mat_dict():
    """
    Load data from viscoelasticity dataset.
    """
    param_df = pd.DataFrame(loadmat(
        'X:/YuxiangWang/DataAnalysis/skinMechanicsAll/analysis/' +
        'ViscoAnalysis052013/strain_level_2py.mat')['qlv2tFixPara'])
    param_df.columns = ['tau1', 'tau2', 'g1', 'g2', 'ginf', 'mu', 'alpha',
                        'r2', 'stretch', 'thickness', 'skin_id', 'ramp_time']
    param_df['skin_id'] = param_df['skin_id'].astype('i')
    param_df['thickness'] *= 1e3  # Change unit to microns
    return param_df


def get_simprop_df(param_df):
    """
    Get statistical values for simulation.
    """
    # Creat the thicknesses and the alphas
    simprop_dict = {}
    prop_list = ['thickness', 'alpha', 'ginf']
    for prop in prop_list:
        simprop_dict[prop] = get_simprop(param_df[prop])
    # Manually adjust ginf and g1, g2
    simprop_dict['ginf'][0] = .1
    p = np.polyfit(param_df['ginf'], param_df['g1'], 1)
    # Calculate p-value for this regression
    print('Stats of ginf and g1 regression:',
          linregress(param_df['ginf'], param_df['g1']))
    simprop_dict['g1'] = np.polyval(p, simprop_dict['ginf'])
    simprop_dict['g2'] = 1. - simprop_dict['g1'] - simprop_dict['ginf']
    # Add sylgard elasticity and thickness
    sylgardh = 10.1348
    sylgarde = 1.05e5
    simprop_dict['sylgardh'] = sylgardh * np.r_[.5:1.5:5j]
    simprop_dict['sylgarde'] = sylgarde * np.r_[.5:1.5:5j]
    simprop_array = np.c_[
        simprop_dict['thickness'], simprop_dict['alpha'],
        simprop_dict['sylgardh'], simprop_dict['sylgarde'],
        simprop_dict['g1'], simprop_dict['g2'], simprop_dict['ginf']]
    # Save to csv for abaqus scripts to load
    np.savetxt('./csvs/simprop.csv', simprop_array, delimiter=',')
    # Save dataframe to excel for the paper
    simprop_df = pd.DataFrame(simprop_dict)
    simprop_df.to_excel('./csvs/simprop.xlsx')
    return simprop_df


def draw_boxplot(param_df, simprop_df, bw_only=False):
    """
    Draw a boxplot for distribution of thickness, modulus and viscoelasticity.
    """
    fig, axs = plt.subplots()
    bp_labels = [r'Thickness ($\mu$m)', 'Modulus', 'Viscoelasticity']
    bp_array = np.c_[param_df.thickness, param_df.alpha, param_df.ginf]
    bp = axs.boxplot(bp_array/bp_array.mean(axis=0), labels=bp_labels)
    bp_feature_array = np.c_[simprop_df.thickness, simprop_df.alpha,
                             simprop_df.ginf]
    bp_feature_array[0, 2] = param_df.ginf.min()
    if bw_only:
        for line in bp.values():
            plt.setp(line, color='k')
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


def get_ra_g(param_df, simprop_df):
    """
    Design data for the relax adapt analysis
    """
    # For the thickness induced changes
    p_ginf = np.polyfit(param_df.thickness, param_df.ginf, 1)
    p_g1 = np.polyfit(param_df.thickness, param_df.g1, 1)
    rathick_ginf = np.polyval(p_ginf, simprop_df['thickness'])
    rathick_g1 = np.polyval(p_g1, simprop_df['thickness'])
    rathick_g2 = 1 - rathick_ginf - rathick_g1
    np.savetxt('./csvs/rathickg.csv', np.c_[
        rathick_g1, rathick_g2, rathick_ginf], delimiter=',')
    # For the individual differences
    residuals = param_df.ginf - np.polyval(p_ginf, param_df.thickness)
    ginf_residuals = get_simprop(residuals)
    raind_ginf = np.median(param_df.ginf) + ginf_residuals
    p_ginf_to_g1 = np.polyfit(param_df.ginf, param_df.g1, 1)
    raind_g1 = np.polyval(p_ginf_to_g1, raind_ginf)
    raind_g2 = 1 - raind_ginf - raind_g1
    np.savetxt('./csvs/raindg.csv', np.c_[
        raind_g1, raind_g2, raind_ginf], delimiter=',')


def get_repsample(param_df, dataset='2013'):
    """
    Get representative samples with a step-wise method.
    """
    # Load dataset
    if dataset == '2013':
        population_data = np.c_[
            param_df.tau1, param_df.tau2, param_df.g1, param_df.g2,
            param_df.ginf, param_df.mu, param_df.alpha, param_df.thickness]
        skin_id_arr = np.unique(param_df.skin_id)
        # Only use the median strain level
        unique_skin_ind = []
        for i in skin_id_arr:
            unique_skin_ind.append(
                np.median(np.nonzero(param_df.skin_id == i)[0]).astype('i'))
        population_data = population_data[unique_skin_ind, :]
    elif dataset == '2011':
        xlsx_df = pd.read_excel(
            'X:/YuxiangWang/WorkArchive/DocumentFolder201507/分析/201404/' +
            'ViscoAnalysis0411.xlsm', sheetname='SummerFast',
            index_col=None, header=None)
        qlv_params = xlsx_df.iloc[5:49, 25:32].values.astype('f')
        thickness = xlsx_df.iloc[5:49, 10].values.astype('f')
        population_data = np.c_[qlv_params, thickness]
    norm_population_data = scale(population_data)
    sample_ind = np.array([])
    covtot = (np.cov(norm_population_data, rowvar=0)**2).sum()
    covres_list = [covtot]
    for i in range(population_data.shape[0]):
        sample_ind = add_sample(norm_population_data, sample_ind)
        covres_list.append(calculate_covres(norm_population_data, sample_ind))
    rel_err = np.array(covres_list) / covtot
    # Plot the convergence rate
    fig, axs = plt.subplots()
    axs.plot(100 * (1 - rel_err), '-k')
    axs.set_title('Population N = %d' % population_data.shape[0])
    axs.set_xlabel('# of samples')
    axs.set_ylabel('% of population accounted for')
    axs.grid()
    fig.tight_layout()
    fig.savefig('./figures/cov_converge.png', dpi=300)
    fig.savefig('./figures/cov_converge.pdf')
    plt.close(fig)
    # Get actual data
    sample_data = population_data[sample_ind[:6], :]
    np.savetxt('./csvs/repsample.csv', sample_data, delimiter=',')
    # Make the dataframe version for paper writing
    columns = ['tau1', 'tau2', 'g1', 'g2', 'ginf', 'mu', 'alpha', 'thickness']
    sample_data_df = pd.DataFrame(sample_data, columns=columns)
    sample_data_df = sample_data_df[['thickness', 'mu', 'alpha',
                                     'tau1', 'tau2', 'g1', 'g2', 'ginf']]
    sample_data_df.index += 1  # Index start from 1 for biologists
    sample_data_df.to_csv('./csvs/repsample_df.csv')
    return sample_data_df


def add_sample(norm_population_data, old_sample_ind):
    """
    Add one sample to the sample index list, that minimizes the difference
    between population and sample covariance matrix.
    """
    if len(old_sample_ind) == 0:
        new_sample_ind = np.array([((
            norm_population_data - norm_population_data.mean(
                axis=0))**2).sum(axis=1).argmin()])
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
    """
    Calculate the squared sum of errors between population and sample
    covariance matrix.
    """
    sample_data = population_data[sample_ind, :]
    population_cov = np.cov(population_data, rowvar=0)
    sample_cov = np.cov(sample_data, rowvar=0)
    covres = ((population_cov - sample_cov)**2).sum()
    return covres


if __name__ == '__main__':
    param_df = load_mat_dict()
    simprop_df = get_simprop_df(param_df)
    draw_boxplot(param_df, simprop_df)
    get_ra_g(param_df, simprop_df)
    sample_data_df = get_repsample(param_df, dataset='2013')
