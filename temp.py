import os
os.chdir('X:\WorkFolder\AbaqusFolder\YoshiModel')
from abqimport import *

jobName = 'temp'

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
# Get contact pressure
cnode_no = len(odb.steps.values()[0].frames[0].fieldOutputs['CPRESS   ASSEMBLY_S_SURF-3/ASSEMBLY_TIP-1_RIGIDSURFACE_'].values)
time = []
cpress, cnodex, cnodeu1, cnodeu2 = [], [], [], []
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

# Get all MCNC outputs
mcncElemSet = odb.rootAssembly.instances['SKIN_SUBSTRATE-1'].elementSets['MCNC_EL']
def getNextMcncElemSet(mcncElemSet):
    elemLabelTuple = tuple([elem.label+1 for elem in mcncElemSet.elements])
    setName = '%s%s'%elemLabelTuple
    for elem in mcncElemSet.elements:
        session.odbs.values()[0].rootAssembly.instances['SKIN_SUBSTRATE-1'].ElementSetFromElementLabels(name=setName, 
            elementLabels=elemLabelTuple)
    return nextMcncElemSet

for i, step in enumerate(odb.steps.values()):
    for frame in step.frames:
        stress.append(-.5*frame.fieldOutputs['S'].getSubset(region=mcncElemSet).values[0].minPrincipal\
            -.5*frame.fieldOutputs['S'].getSubset(region=mcncElemSet).values[1].minPrincipal)
        strain.append(-.5*frame.fieldOutputs['LE'].getSubset(region=mcncElemSet).values[0].minPrincipal\
            -.5*frame.fieldOutputs['LE'].getSubset(region=mcncElemSet).values[1].minPrincipal)    
        sener.append(.5*frame.fieldOutputs['SENER'].getSubset(region=mcncElemSet).values[0].data\
            +.5*frame.fieldOutputs['SENER'].getSubset(region=mcncElemSet).values[1].data)


    
rpNode = odb.rootAssembly.instances['TIP-1'].nodes[0]
mcncElemSet = odb.rootAssembly.instances['SKIN_SUBSTRATE-1'].elementSets['MCNC_EL']
time, force, displ, stress, strain, sener = [], [], [], [], [], []


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


