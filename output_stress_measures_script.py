import os
os.chdir('X:/WorkFolder/AbaqusFolder/YoshiModel')
from readodb import getAllStresses

for i in range(5):
    jobName = 'SkinThick2%dDispl' % i
    getAllStresses(jobName)

