import os
os.chdir('X:\YuxiangWang\AbaqusFolder\YoshiModel')
from abqimport import *
from readodb import getSurfaceDistribution

for fname in os.listdir('./odbs'):
    if fname.endswith('.odb') and fname.startswith('S'):
        getSurfaceDistribution(fname[:-4])