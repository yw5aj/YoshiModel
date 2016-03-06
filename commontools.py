from abqimport import *
import os, shutil
import numpy as np


def writeLine(filePath, line):
    """
    Write a list of data to a line, delimited by comma, and appended to a file.
    
    Parameters
    ----------
    filePath : str
        Path to the file to be appended / created.
    
    line : list
        The data to be written.
    """
    with open(filePath, 'a+') as f:
        for word in line:
            f.write(str(word) + ',')
        f.write('\n')
    return


def deleteJob(jobName, clearMdb=False):
    """
    Delete the job in mdb and associated files. Return a new name if conflict 
    is detected.
    """
    if jobName in mdb.jobs.keys() and clearMdb:
        del mdb.jobs[jobName]
    for fileName in os.listdir('.'):
        if fileName.startswith(jobName):
            try:
                os.remove(fileName)
            except WindowsError:
                jobName = jobName + '1'
    return jobName


def transferFile(jobName, fileExt):
    """
    Transfer the file to the corresponding folder.
    """
    fname_src = '%s.%s' % (jobName, fileExt)
    fname_dst = '%ss/%s.%s' % (fileExt, jobName, fileExt)
    try:
        shutil.move(fname_src, fname_dst)
    except WindowsError:
        try:
            shutil.copy2(fname_src, fname_dst)
        except:
            pass
    return


def deleteModel(modelName):
    try:
        del mdb.models[modelName]
    except KeyError:
        pass
    return


def submitJob(modelName, jobName, fakeRun=False):
    """
    Create job from model and submit this job.
    
    Parameters
    ----------
    modelName : str
        Name of the model in current mdb.
    jobName : str
        Name of the job being submitted
    fakeRun : bool
        Skip actually running the model if True. For debugging purpose only.
    """
    mdb.Job(name=jobName, model=modelName, description='', 
        type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, 
        memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', multiprocessingMode=DEFAULT, numCpus=1, numGPUs=0)
    if not fakeRun:
        mdb.jobs[jobName].submit(consistencyChecking=OFF)
    return


def getR2(expData, modelData):
    """
    Get R-squared value between model and experiment.
    
    Parameters
    ----------
    expData : ndarray
        1D data acquired from experiment.
    modelData : ndarray
        1D data acquired from computational model. modelData.shape[0] should be
        greater than expData.shape[0] to cover the whole range to avoid np.nan.
    
    Returns
    -------
    r2 : float
        The R-squared value.
    """
    modelData = modelData[modelData[:, 0].argsort()]
    interpData = expData.copy()
    interpData[:,1] = np.interp(expData[:, 0], modelData[:, 0], modelData[:, 1])
    sst = np.var(expData[:,1])*expData.shape[0]
    sse = (np.linalg.norm(expData[:,1]-interpData[:,1]))**2
    r2 = 1. -sse/sst
    return r2





def plotInCae(data1, data2, save_data=False, **kwargs):
    """
    Plot 2 curves in CAE, and save plotted data as csv and figuure as png.
    
    Parameters
    ----------
    data1, data2 : ndarray
        2D data to be plotted, where 1st col is x and 2nd col is y. If data2 
        is not passed in, then two overlappting data1 will be plotted.
    save_data : bool, optional
        Whether to save the data, default to be False.
    filePath : str, optional
        File name to be saved for both .csv and .png. Default filename is tmp.
    xlim, ylim: tuple, optional
        Range of the x and y axis, if set.
    """
    # Check whether data2 is passed in
    if data2 is None:
        data2 = data1
    session.XYData(data=data1, name='xyData1', legendLabel='Data 1')
    session.XYData(data=data2, name='xyData2', legendLabel='Data 2')
    if len(session.xyPlots)==0:
        x = session.XYPlot('XYPlot-1')
    else:
        x = session.xyPlots['XYPlot-1']
    session.viewports['Viewport: 1'].setValues(displayedObject=x)
    xyp = session.xyPlots['XYPlot-1']
    chartName = xyp.charts.keys()[0]
    chart = xyp.charts[chartName]
    xy1 = session.xyDataObjects['xyData1']
    c1 = session.Curve(xyData=xy1)
    xy2 = session.xyDataObjects['xyData2']
    c2 = session.Curve(xyData=xy2)
    chart.setValues(curvesToPlot=(c1, c2, ), )
    if 'xlim' in kwargs:
        xmin, xmax = kwargs['xlim']
        session.charts['Chart-1'].axes1[0].axisData.setValues(maxValue=xmax, 
            maxAutoCompute=False)
        session.charts['Chart-1'].axes1[0].axisData.setValues(minValue=xmin, 
            minAutoCompute=False)
    if 'ylim' in kwargs:
        ymin, ymax = kwargs['ylim']
        session.charts['Chart-1'].axes2[0].axisData.setValues(maxValue=ymax, 
            maxAutoCompute=False)
        session.charts['Chart-1'].axes2[0].axisData.setValues(minValue=ymin, 
            minAutoCompute=False)
    session.mdbData.summary()
    # Save the data to csv and png file
    if save_data:
        if 'filePath' in kwargs:
            filePath = kwargs['filePath']
        else:
            filePath = './fig/tmp'
        dirPath = os.path.dirname(filePath)
        if not os.path.isdir(dirPath):
            os.makedirs(dirPath)
        np.savetxt(filePath+'data1.csv', data1, delimiter=',')
        np.savetxt(filePath+'data2.csv', data2, delimiter=',')
        session.printToFile(fileName=filePath+'.png', format=PNG, 
            canvasObjects=(session.viewports['Viewport: 1'], ))
    return

