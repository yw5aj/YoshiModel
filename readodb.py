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


def getSurfaceDistribution(jobName):
    # Open the odb file
    if os.path.exists('./'+jobName+'.odb'):
        odb = session.openOdb('./'+jobName+'.odb', readOnly=True)
    else:
        odb = session.openOdb('./odbs/'+jobName+'.odb', readOnly=True)
    # Get duration of each step
    stepTime = [0]
    for step in odb.steps.values():
        stepTime.append(step.frames[-1].frameValue)
    stepTime = np.cumsum(stepTime)
    # Get all MCNC sets
    mcncElemSet = odb.rootAssembly.instances['SKIN_SUBSTRATE-1'].elementSets['MCNC_EL']
    def getNextMcncElemSet(mcncElemSet):
        elemLabelTuple = tuple([elem.label+1 for elem in mcncElemSet.elements])
        setName = '%s%s'%elemLabelTuple
        nextMcncElemSet = session.odbs.values()[0].rootAssembly.instances['SKIN_SUBSTRATE-1'].ElementSetFromElementLabels(name=setName, 
            elementLabels=elemLabelTuple)
        return nextMcncElemSet
    mcncElemSetList = [mcncElemSet]
    # Note that celem_no = cnode_no - 1
    for i in range(cnode_no-2):
        mcncElemSetList.append(getNextMcncElemSet(mcncElemSetList[-1]))
    cnode_no = len(odb.steps.values()[0].frames[0].fieldOutputs['CPRESS   ASSEMBLY_S_SURF-3/ASSEMBLY_TIP-1_RIGIDSURFACE_'].values)
    time = []
    cpress, cnodex, cnodeu1, cnodeu2 = [], [], [], []
    xcoordOldList, xcoordNewList, stressList, strainList, senerList = [], [], [], [], []
    # Iterate through frames to get data
    for i, step in enumerate(odb.steps.values()):
        for frame in step.frames:
            time.append(stepTime[i]+frame.frameValue)
            # Fill contact data
            cpress.append([])
            cnodex.append([])
            cnodeu1.append([])
            cnodeu2.append([])
            for j in range(cnode_no):
                value = frame.fieldOutputs['CPRESS   ASSEMBLY_S_SURF-3/ASSEMBLY_TIP-1_RIGIDSURFACE_'].values[j]
                cpress[-1].append(value.data)
                node = odb.rootAssembly.instances['SKIN_SUBSTRATE-1'].nodes[value.nodeLabel-1]
                cnodex[-1].append(node.coordinates[0])
                cnodeu1[-1].append(frame.fieldOutputs['U'].getSubset(region=node).values[0].data[0])
                cnodeu2[-1].append(frame.fieldOutputs['U'].getSubset(region=node).values[0].data[1])
            # Get MCNC data
            xcoordOldList.append([])
            xcoordNewList.append([])
            stressList.append([])
            strainList.append([])
            senerList.append([])
            def getMcncElemSetOutput(mcncElemSet):
                def getXcoordFromMcncElemSet(mcncElemSet):
                    nodeSet = [odb.rootAssembly.instances['SKIN_SUBSTRATE-1'].nodes[nodeLabel-1] for nodeLabel in mcncElemSet.elements[0].connectivity]
                    xcoordOldList = [node.coordinates[0] for node in nodeSet]
                    xDisplList = [frame.fieldOutputs['U'].getSubset(region=node).values[0].data[0] for node in nodeSet]
                    xcoordOld = np.mean(xcoordOldList)
                    xcoordNew = np.mean(np.array(xcoordOldList) + np.array(xDisplList))
                    return xcoordOld, xcoordNew
                xcoordOld, xcoordNew = getXcoordFromMcncElemSet(mcncElemSet)
                stress = -.5*frame.fieldOutputs['S'].getSubset(region=mcncElemSet).values[0].minPrincipal\
                    -.5*frame.fieldOutputs['S'].getSubset(region=mcncElemSet).values[1].minPrincipal
                strain = -.5*frame.fieldOutputs['LE'].getSubset(region=mcncElemSet).values[0].minPrincipal\
                    -.5*frame.fieldOutputs['LE'].getSubset(region=mcncElemSet).values[1].minPrincipal
                sener = .5*frame.fieldOutputs['SENER'].getSubset(region=mcncElemSet).values[0].data\
                    +.5*frame.fieldOutputs['SENER'].getSubset(region=mcncElemSet).values[1].data
                return xcoordOld, xcoordNew, stress, strain, sener
            for mcncElemSet in mcncElemSetList:
                xcoordOld, xcoordNew, stress, strain, sener = getMcncElemSetOutput(mcncElemSet)
                xcoordOldList[-1].append(xcoordOld)
                xcoordNewList[-1].append(xcoordNew)
                stressList[-1].append(stress)
                strainList[-1].append(strain)
                senerList[-1].append(sener)
    odb.close()
    # Save data to csv
    np.savetxt('./csvs/%s_time.csv'%jobName, time, delimiter=',')
    np.savetxt('./csvs/%s_cpress.csv'%jobName, cpress, delimiter=',')
    np.savetxt('./csvs/%s_cxold.csv'%jobName, cnodex, delimiter=',')
    np.savetxt('./csvs/%s_cy.csv'%jobName, cnodeu2, delimiter=',')
    np.savetxt('./csvs/%s_cxnew.csv'%jobName, np.array(cnodex)+np.array(cnodeu1), delimiter=',')
    np.savetxt('./csvs/%s_mcncxold.csv'%jobName, xcoordOldList, delimiter=',')
    np.savetxt('./csvs/%s_mcncxnew.csv'%jobName, xcoordNewList, delimiter=',')
    np.savetxt('./csvs/%s_mcncstress.csv'%jobName, stressList, delimiter=',')
    np.savetxt('./csvs/%s_mcncstrain.csv'%jobName, strainList, delimiter=',')
    np.savetxt('./csvs/%s_mcncsener.csv'%jobName, senerList, delimiter=',')
    return