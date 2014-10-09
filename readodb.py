from abqimport import *
import numpy as np
import os
from commontools import *


def getOutputs(jobName, save2csv=True):
    if os.path.exists('./'+jobName+'.odb'):
        odb = session.openOdb('./'+jobName+'.odb', readOnly=True)
    else:
        odb = session.openOdb('./odbs/'+jobName+'.odb', readOnly=True)
    rpNode = odb.rootAssembly.instances['TIP-1'].nodes[0]
    mcncElemSet = odb.rootAssembly.instances['SKIN_SUBSTRATE-1'].elementSets['MCNC_EL']
    time, force, displ, stress, strain, sener = [], [], [], [], [], []
    stepTime = [0]
    for step in odb.steps.values():
        stepTime.append(step.frames[-1].frameValue)
    stepTime = np.cumsum(stepTime)
    for i, step in enumerate(odb.steps.values()):
        for frame in step.frames:
            time.append(stepTime[i]+frame.frameValue)
            if jobName.endswith('Force'):
                force.append(-frame.fieldOutputs['CF'].getSubset(region=rpNode).values[0].data[1])
            else:
                force.append(-frame.fieldOutputs['RF'].getSubset(region=rpNode).values[0].data[1])
            displ.append(-frame.fieldOutputs['U'].getSubset(region=rpNode).values[0].data[1])
            stress.append(-.5*frame.fieldOutputs['S'].getSubset(region=mcncElemSet).values[0].minPrincipal\
                -.5*frame.fieldOutputs['S'].getSubset(region=mcncElemSet).values[1].minPrincipal)
            strain.append(-.5*frame.fieldOutputs['LE'].getSubset(region=mcncElemSet).values[0].minPrincipal\
                -.5*frame.fieldOutputs['LE'].getSubset(region=mcncElemSet).values[1].minPrincipal)    
            sener.append(.5*frame.fieldOutputs['SENER'].getSubset(region=mcncElemSet).values[0].data\
                +.5*frame.fieldOutputs['SENER'].getSubset(region=mcncElemSet).values[1].data)
    time = np.array(time)
    force = np.array(force)
    displ = np.array(displ)
    stress = np.array(stress)
    strain = np.array(strain)
    sener = np.array(sener)
    if save2csv:
        np.savetxt('./csvs/'+jobName+'.csv', np.column_stack((time, force, displ, stress, strain, sener)), delimiter=',')
    odb.close()
    return time, force, displ, stress, strain, sener


def getStaticForceDispl(timeList, forceList, displList):
    staticDisplList = [0.]
    staticForceList = [0.]
    for i, time in enumerate(timeList):
        force = forceList[i]
        displ = displList[i]
        maxForceTime = time[force.argmax()]
        staticTime = np.r_[maxForceTime+2.:maxForceTime+4.5:1e-3]
        staticForceList.append(np.interp(staticTime, time, force).mean())
        staticDisplList.append(np.interp(staticTime, time, displ).mean())
    staticDisplList = np.array(staticDisplList)
    staticForceList = np.array(staticForceList)
    return staticForceList, staticDisplList

