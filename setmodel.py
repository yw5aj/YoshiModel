from abqimport import *
import numpy as np

a_ramp_curve = -1.04
a1_ramp_time_map = 5.51e-4
a0_ramp_time_map = 0.138


def setThickness(modelName, skin=418.5, nylon=338.8, sylgard=10.1348):
    """
    Set the thickness of each layer. Note the units: skin & nylon in microns and sylgard in mm.
    """
    # Convert layer thicknesses to cumulative thickness in right units
    skin_m = skin * 1e-6
    nylon_m = nylon * 1e-6
    sylgard_m = sylgard * 1e-3
    all_layers = skin_m + nylon_m + sylgard_m
    ## Start of the abaqus code
    model = mdb.models[modelName]
    # Edit the geometry and remesh
    p = mdb.models[modelName].parts['skin_substrate']
    s = p.features['Shell planar-1'].sketch
    mdb.models[modelName].ConstrainedSketch(name='__edit__', objectToCopy=s)
    s1 = mdb.models[modelName].sketches['__edit__']
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=SUPERIMPOSE)
    p.projectReferencesOntoSketch(sketch=s1, 
        upToFeature=p.features['Shell planar-1'], filter=COPLANAR_EDGES)
    d[0].setValues(value=all_layers, )
    s1.unsetPrimaryObject()
    p = mdb.models[modelName].parts['skin_substrate']
    p.features['Shell planar-1'].setValues(sketch=s1)
    del mdb.models[modelName].sketches['__edit__']
    p = mdb.models[modelName].parts['skin_substrate']
    # Must comment out this step incase sylgard gets too thin, then before d[1] and d[2] got reset the part cannot regenerate
    # p.regenerate()
    p = mdb.models[modelName].parts['skin_substrate']
    s = p.features['Partition face-1'].sketch
    mdb.models[modelName].ConstrainedSketch(name='__edit__', objectToCopy=s)
    s2 = mdb.models[modelName].sketches['__edit__']
    g, v, d, c = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
    s2.setPrimaryObject(option=SUPERIMPOSE)
    p.projectReferencesOntoSketch(sketch=s2, 
        upToFeature=p.features['Partition face-1'], filter=COPLANAR_EDGES)
    d[1].setValues(value=sylgard_m, )
    d[2].setValues(value=nylon_m, )
    s2.unsetPrimaryObject()
    p = mdb.models[modelName].parts['skin_substrate']
    p.features['Partition face-1'].setValues(sketch=s2)
    del mdb.models[modelName].sketches['__edit__']
    p = mdb.models[modelName].parts['skin_substrate']
    p.regenerate()
    p = mdb.models[modelName].parts['skin_substrate']
    p.generateMesh()
    # Translate the assembly to make surface at origin
    currentY = model.rootAssembly.instances['tip-1'].vertices[4].pointOn[0][1]
    a = mdb.models[modelName].rootAssembly
    a.translate(instanceList=('skin_substrate-1', 'tip-1'), vector=(0.0, -currentY, 
        0.0))
    # Select the MCNC nodes and elements
    elements = model.rootAssembly.instances['skin_substrate-1'].elements.getByBoundingBox(xMax=9e-6, yMin=-40e-6)
    assert len(elements) == 2, "Element set MCNC_el contains %d elements, instead of 2."%len(elements)
    elemLabels = []
    for elem in elements:
        elemLabels.append(elem.label)
    p = model.parts['skin_substrate']
    e = p.elements
    elements = e.sequenceFromLabels(labels=elemLabels)
    p.Set(elements=elements, name='MCNC_el')
    a = model.rootAssembly
    a.regenerate()
    return


def set_skin_property_qlv(modelName, g_array, tau_array, mu, alpha):
    model = mdb.models[modelName]
    # Clear keywordBlock in case any previous PNV models exist
    model.keywordBlock.setValues(edited=False)
    model.keywordBlock.synchVersions()
    # Set the QLV model
    mdb.models[modelName].materials['skin'].Hyperelastic(materialType=ISOTROPIC, 
        testData=OFF, type=OGDEN, moduliTimeScale=INSTANTANEOUS, 
        volumetricResponse=VOLUMETRIC_DATA, table=((mu, alpha, 1./mu/10.), ))
    mdb.models[modelName].materials['skin'].Viscoelastic(domain=TIME, 
        time=PRONY, table=((g_array[1], 0.0, tau_array[1]), (g_array[2], 0.0, tau_array[2]))) 
    return


def set_sylgard_property(modelName, g, tau, c10):
    mdb.models[modelName].materials['sylgard'].hyperelastic.setValues(table=((
        c10, 1./2/c10), ))
    mdb.models[modelName].materials['sylgard'].viscoelastic.setValues(
        domain=TIME, time=PRONY, table=((g, 0.0, tau), ))
    return


def setStepTime(modelName, stepName, stepTime):
    mdb.models[modelName].steps[stepName].setValues(timePeriod=stepTime, cetol=0.01)
    return


def setAllStepTimes(modelName, rampLiftTime, holdTime=5.):
    for stepName in ['ramp', 'lift']:
        if stepName in mdb.models[modelName].steps.keys():
            setStepTime(modelName, stepName, rampLiftTime)
    setStepTime(modelName, 'hold', holdTime)
    return


def setHoldDispl(modelName, holdDispl, setTime=True):
    """
    The holdDispl should be positive, in mm.
    """
    mdb.models[modelName].boundaryConditions['movingIndenter'].setValues(
        u2=-1e-3*holdDispl)
    return


def deleteLiftStep(modelName):
    del mdb.models[modelName].steps['lift']
    return


def setRampCurve(modelName, rampLiftTime, a=a_ramp_curve):
    xdata = np.r_[0:1:20j]
    ydata = a * xdata**2 + (1. - a) * xdata
    xdata_scaled = np.r_[0:rampLiftTime:20j]
    rampCurve = np.column_stack((xdata_scaled, ydata))
    liftCurve = np.column_stack((xdata_scaled, ydata[::-1]))
    rampCurve = tuple(map(tuple, rampCurve))
    liftCurve = tuple(map(tuple, liftCurve))
    mdb.models[modelName].TabularAmplitude(name='RampCurve', timeSpan=STEP, 
        smooth=SOLVER_DEFAULT, data=rampCurve)
    mdb.models[modelName].TabularAmplitude(name='LiftCurve', timeSpan=STEP, 
        smooth=SOLVER_DEFAULT, data=liftCurve)        
    if 'Displ' in modelName:
        mdb.models[modelName].boundaryConditions['movingIndenter'].setValues(
            amplitude='RampCurve')
        mdb.models[modelName].boundaryConditions['movingIndenter'].setValuesInStep(
            stepName='lift', amplitude='LiftCurve')
    elif 'Force' in modelName:
        mdb.models[modelName].loads['forceLoad'].setValues(amplitude='RampCurve')
        if 'lift' in mdb.models[modelName].steps.keys():
            mdb.models[modelName].loads['forceLoad'].setValuesInStep(stepName='lift', 
                amplitude='LiftCurve')
    return    


def copyToForce(displModelName, rampLiftTime, holdForce):
    modelName = displModelName.replace('Displ', 'Force')
    mdb.Model(modelName, objectToCopy=mdb.models[displModelName])
    # Remove displ control
    del mdb.models[modelName].boundaryConditions['movingIndenter']
    # Add force load
    a = mdb.models[modelName].rootAssembly
    r1 = a.instances['tip-1'].referencePoints
    refPoints1=(r1[2], )
    region = a.Set(referencePoints=refPoints1, name='Set-7')
    mdb.models[modelName].ConcentratedForce(name='forceLoad', 
        createStepName='ramp', region=region, cf2=-holdForce, amplitude='RampCurve', 
        distributionType=UNIFORM, field='', localCsys=None)
    # Update step time and ramp curve
    setAllStepTimes(modelName, rampLiftTime)
    setRampCurve(modelName, rampLiftTime)
    return modelName