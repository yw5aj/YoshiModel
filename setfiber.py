from abqimport import *
from setmodel import *
from commontools import *
from readodb import *
from feconstants import *

def getStimBlockFromCsv(filePath):
    rampLiftTimeArray, holdDisplArray = np.genfromtxt(filePath, delimiter=',').T
    stimBlock = {'rampLiftTimeArray': rampLiftTimeArray, 'holdDisplArray': holdDisplArray}
    return stimBlock


def getRampLiftTimeArray(holdDisplArray):
    return np.polyval(displtimecoeff, holdDisplArray)


def getRampLiftTimeArrayForce(holdForceArray):
    eqdisp = np.interp(holdForceArray, displforce[:, 1], displforce[:, 0]*1e3)
    return np.polyval(displtimecoeff, eqdisp)


def setHoldDisplArray(holdDisplArray, stimBlock=None):
    if stimBlock is None:
        stimBlock = copy.deepcopy(stimBlockDefault)
    stimBlock['holdDisplArray'] = holdDisplArray
    stimBlock['rampLiftTimeArray'] = getRampLiftTimeArray(holdDisplArray)
    return stimBlock


def setHoldForceArray(holdForceArray, stimBlockForce=None):
    if stimBlockForce is None:
        stimBlockForce = copy.deepcopy(stimBlockDefaultForce)
    stimBlockForce['holdForceArray'] = holdForceArray
    stimBlockForce['rampLiftTimeArray'] = getRampLiftTimeArrayForce(holdForceArray)
    return stimBlockForce


class Fiber:

    def __init__(self, baseModelName='temp', suffix='Displ', stimBlock=stimBlockDefault, materialBlock=materialBlockDefault, skipWait=False, runFiber=True, doAnalysis=False):
        self.finishFlag = False
        for key, value in stimBlock.items():
            setattr(self, key, value)
        assert len(self.rampLiftTimeArray) == len(self.holdDisplArray), "Ramp time and displacement load does not match."
        for key, value in materialBlock.items():
            setattr(self, key, value)
        self.openBaseCae()
        self.baseModelName = baseModelName
        modelNameList = [baseModelName+str(i)+suffix for i in range(len(stimBlock.values()[0]))]
        self.modelList = []
        for i, modelName in enumerate(modelNameList):
            stimLine = {'rampLiftTime': self.rampLiftTimeArray[i], 'holdDispl': self.holdDisplArray[i]}
            self.modelList.append(Model(modelName, stimLine, materialBlock))
        if runFiber:
            self.runFiber(skipWait=skipWait)
            self.getStaticForceDispl()
        elif doAnalysis:
            self.doAnalysis()
        self.finishFlag = True

    def runFiber(self, skipWait=False):
        for model in self.modelList:
            model.runModel()
            if not skipWait:
                model.waitForCompletion()
        if skipWait:
            for model in self.modelList:
                model.waitForCompletion()
        for model in self.modelList:
            model.extractOutputs()
        for model in self.modelList:
            model.transferFile('odb')
            model.transferFile('inp')
            model.deleteJob()

    def doAnalysis(self):
        for model in self.modelList:
            model.extractOutputs()
        self.getStaticForceDispl()

    def openBaseCae(self, caeFile='base_model_20150506'):
        caeFilePath = './CaeFiles/' + caeFile + '.cae'
        openMdb(pathName=caeFilePath)

    def getStaticForceDispl(self):
        self.timeList = [model.time for model in self.modelList]
        self.forceList = [model.force for model in self.modelList]
        self.displList = [model.displ for model in self.modelList]
        self.staticForceList, self.staticDisplList = getStaticForceDispl(self.timeList, self.forceList, self.displList)


class Model:

    def __init__(self, modelName, stimLine=stimLineDefault, materialBlock=materialBlockDefault):
        for key, value in stimLine.items():
            setattr(self, key, value)
        for key, value in materialBlock.items():
            setattr(self, key, value)
        self.modelName = modelName
        self.setUpModel()

    def setUpModel(self):
        self.copyModel()
        setCylinderRadius(self.modelName, self.cylinderRadius)
        setThickness(self.modelName, *self.thicknessAll)
        self.setMaterialProperties()
        setAllStepTimes(self.modelName, self.rampLiftTime)
        setRampCurve(self.modelName, self.rampLiftTime)
        setHoldDispl(self.modelName, self.holdDispl)
        deleteLiftStep(self.modelName) # Skipping this to save model execution time - not using it now anyway

    def setMaterialProperties(self):
        set_skin_property_qlv(self.modelName, self.skin_g_array, self.skin_tau_array, self.skin_mu, self.skin_alpha)
        set_sylgard_property(self.modelName, self.sylgard_g, self.sylgard_tau, self.sylgard_c10)

    def copyModel(self):
        mdb.Model(name=self.modelName, objectToCopy=mdb.models['base_model'])

    def runModel(self):
        if self.modelName not in mdb.jobs:
            mdb.Job(name=self.modelName, model=self.modelName, description='',
                type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None,
                memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
                explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
                modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
                scratch='', multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
        mdb.jobs[self.modelName].submit(consistencyChecking=OFF)

    def waitForCompletion(self):
        mdb.jobs[self.modelName].waitForCompletion()

    def extractOutputs(self):
        self.time, self.force, self.displ, self.stress, self.strain, self.sener = getOutputs(self.modelName)

    def transferFile(self, fileExt):
        transferFile(self.modelName, fileExt)

    def deleteJob(self):
        deleteJob(self.modelName)


class FiberForce(Fiber):

    def __init__(self, displFiber, stimBlock=stimBlockDefaultForce, skipWait=False, runFiber=True, doAnalysis=False):
        self.finishFlag = False
        self.modelList = []
        for i, displModel in enumerate(displFiber.modelList):
            rampLiftTime = stimBlock['rampLiftTimeArray'][i]
            holdForce = stimBlock['holdForceArray'][i]
            self.modelList.append(ModelForce(displModel, rampLiftTime, holdForce))
        if runFiber:
            self.runFiber(skipWait=skipWait)
            self.getStaticForceDispl()
        elif doAnalysis:
            self.doAnalysis()
        self.finishFlag = True


class ModelForce(Model):

    def __init__(self, displModel, rampLiftTime, holdForce):
        self.modelName = copyToForce(displModel.modelName, rampLiftTime, holdForce)
