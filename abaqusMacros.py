# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

def Macro1():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    mdb.openAuxMdb(
        pathName='x:/WorkFolder/AbaqusFolder/YoshiModel/OldModel/ToHValidation0122.cae')
    mdb.copyAuxMdbModel(fromName='2', toName='2')
    mdb.closeAuxMdb()
    del mdb.models['Model-1']
    p = mdb.models['2'].parts['skin_substrate']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)


def Macro2():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    pass


def Macro3():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    a = mdb.models['FitFem0'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON, 
        predefinedFields=ON, connectors=ON)
    mdb.models['FitFem0'].TabularAmplitude(name='Amp-2', timeSpan=STEP, 
        smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (0.5, 0.5), (1.0, 1.0)))


def Macro4():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0335393, 
        farPlane=0.0401451, width=0.0285057, height=0.0170104, 
        viewOffsetX=0.000533035, viewOffsetY=0.000320912)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON, 
        predefinedFields=ON, connectors=ON, adaptiveMeshConstraints=OFF)
    del mdb.models['FitFem0Force'].boundaryConditions['movingIndenter']
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0352995, 
        farPlane=0.0383849, width=0.0118594, height=0.00707695, 
        viewOffsetX=-0.00307155, viewOffsetY=0.00291155)
    a = mdb.models['FitFem0Force'].rootAssembly
    r1 = a.instances['tip-1'].referencePoints
    refPoints1=(r1[2], )
    region = a.Set(referencePoints=refPoints1, name='Set-7')
    mdb.models['FitFem0Force'].ConcentratedForce(name='forceLoad', 
        createStepName='ramp', region=region, cf2=-0.01, amplitude='RampCurve', 
        distributionType=UNIFORM, field='', localCsys=None)


def Macro6():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    session.viewports['Viewport: 1'].odbDisplay.setFrame(step='ramp')


