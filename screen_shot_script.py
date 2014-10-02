#%% For the paper
from abaqus import *
from abaqusConstants import *
# Load output library
o1 = session.openOdb(
    name='X:/WorkFolder/AbaqusFolder/YoshiModel/odbs/SkinAlpha22Displ.odb')
session.viewports['Viewport: 1'].setValues(displayedObject=o1) 
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_DEF, ))   
# Set screen location
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0377807, 
    farPlane=0.0545155, width=0.00143955, height=0.00159838, 
    viewOffsetX=-0.00363814, viewOffsetY=0.00325194)
# Set details
session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
    compass=OFF, title=OFF, state=OFF, annotations=OFF, legendBox=OFF,
    legendNumberFormat=FIXED)
session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
    contourStyle=CONTINUOUS, spectrum='Reversed rainbow')
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(INVARIANT, 
    'Min. Principal'), )
# Save eps
session.epsOptions.setValues(fontType=PS_ALWAYS, shadingQuality=EXTRA_FINE)
session.printToFile(
    fileName='X:/WorkFolder/AbaqusFolder/YoshiModel/figures/screenshot.eps', 
    format=EPS, canvasObjects=(session.viewports['Viewport: 1'], ))
# Save png
session.pngOptions.setValues(imageSize=(3000, 3337))
session.printOptions.setValues(reduceColors=False)
session.printToFile(
    fileName='X:/WorkFolder/AbaqusFolder/YoshiModel/figures/screenshoot', 
    format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))
# Zoom in and save png again
session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0380141, 
    farPlane=0.0542822, width=0.000147796, height=0.0001, 
    viewOffsetX=-0.00408086, viewOffsetY=0.00355891)
session.pngOptions.setValues(imageSize=(3000, 3337))
session.printOptions.setValues(reduceColors=False)
session.printToFile(
    fileName='X:/WorkFolder/AbaqusFolder/YoshiModel/figures/screenshoot_zoomed_in', 
    format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))

#%% For understanding stress distribution
from abaqus import *
from abaqusConstants import *
def screenshot(jobName):
    # Load output library
    o1 = session.openOdb(
        name='X:/WorkFolder/AbaqusFolder/YoshiModel/odbs/%s.odb' % jobName)
    session.viewports['Viewport: 1'].setValues(displayedObject=o1) 
    session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
        CONTOURS_ON_DEF, ))   
    # Set screen location
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0377807, 
        farPlane=0.0545155, width=0.00143955, height=0.00159838, 
        viewOffsetX=-0.00363814, viewOffsetY=0.00325194)
    # Set details
    session.viewports['Viewport: 1'].viewportAnnotationOptions.setValues(
        compass=OFF, title=OFF, state=OFF, annotations=OFF, legendBox=OFF,
        legendNumberFormat=FIXED)
    session.viewports['Viewport: 1'].odbDisplay.contourOptions.setValues(
        contourStyle=CONTINUOUS, spectrum='Reversed rainbow')
    session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
        variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(INVARIANT, 
        'Min. Principal'), )
    # Save png
    session.pngOptions.setValues(imageSize=(3000, 3337))
    session.printOptions.setValues(reduceColors=False)
    session.printToFile(
        fileName='X:/WorkFolder/AbaqusFolder/YoshiModel/figures/screenshoot'+jobName, 
        format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))
    # Zoom in and save png again
    session.viewports['Viewport: 1'].view.setValues(nearPlane=0.0380141, 
        farPlane=0.0542822, width=0.000147796, height=0.0001, 
        viewOffsetX=-0.00408086, viewOffsetY=0.00355891)
    session.pngOptions.setValues(imageSize=(3000, 3337))
    session.printOptions.setValues(reduceColors=False)
    session.printToFile(
        fileName='X:/WorkFolder/AbaqusFolder/YoshiModel/figures/screenshoot_zoomed_in'+jobName, 
        format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))
    return
jobNameList = ['SkinThick%d2Force' % i for i in range(5)]
for jobName in jobNameList:
    screenshot(jobName)