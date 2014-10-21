import numpy as np
import pandas as pd

def convert(fname, oname):
    
    return


if __name__ == '__main__':
    fname_list = ['Fiber5Output%d.csv' % i for i in range(5)]
    oname_list = ['Fiber5Output%d-Steven.csv' % i for i in range(5)]
    for i, fname in enumerate(fname_list):
        convert(fname, oname_list[i])

fname = fname_list[0]
# Read ABAQUS data
df = pd.read_csv(fname, names=['time', 'force', 'displ', 'stress', 'strain', 
                               'sener'])
# Adjust displacement
displcoeff = np.genfromtxt(
    'X:/WorkFolder/DataAnalysis/YoshiRecordingData/csvs/displcoeff.csv', 
    delimiter=',')
displcoeff[0] *= 1e-6
df.displ = df.displ * displcoeff[1] + displcoeff[0]
# Adjust ramp time
peak_index = (df.displ.diff()>0).nonzero()[0][-1]
ramp_time = df.time[peak_index] * displcoeff[1]

