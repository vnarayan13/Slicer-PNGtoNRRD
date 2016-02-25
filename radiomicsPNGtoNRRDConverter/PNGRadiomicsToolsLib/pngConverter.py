from __future__ import print_function
from __main__ import vtk, qt, ctk, slicer, os

import vtkITK
import numpy
import SimpleITK as sitk
import sitkUtils as su
import vtk.util.numpy_support
import collections
import itertools
import math
import string
import operator
import glob
import shutil

import fnmatch
import pdb
import radiomicsDatabase


def Execute(self, inputdir, outputdir, fileIdentifierSettings, applyButton):
  from datetime import datetime
  progress_filename = str(datetime.now().strftime(('%Y-%m-%d_%H-%M-%S')) + '_XYZSnapshot.txt')
  printfile = open(str(os.path.join(outputdir,progress_filename)),mode='a')
  print(fileIdentifierSettings[0], file=printfile)
  
  PatientDirs, PatientNames = radiomicsDatabase.getFolderList(self,inputdir,excludeDirName=False)
  for x,patientName in enumerate(PatientNames):
    print(x,patientName,PatientDirs[x])
    """
    if os.path.exists(os.path.join(outputdir,patientName)):
      radiomicsDatabase.deleteDataSlicer(self)
      slicer.mrmlScene.Clear(0)
      continue
    """  
    #get button widget by reference and change text to x value
    applyButton.text = ("Processing: " + str(x+1) + " of " + str(len(PatientNames)))
    applyButton.repaint()
    #slicer.app.processEvents()
    
    # Set ID current patient
    IDcurrPatient = radiomicsDatabase.getIDcurrPatient(self,2,PatientDirs[x])
    
    #if not os.path.exists(str(os.path.join(outputdir, IDcurrPatient))):
    print("\n" + "Loading Data: " + str(self.IDcurrPatient) + " at location: " + str(PatientDirs[x]),file=printfile)
    
    ExtractionDirs = []
    includeSubfolders = True
    subfoldersIndependent = True
    # Normal or Treat each subfolder as independent scans (option GUI)
    if subfoldersIndependent: ExtractionDirs = radiomicsDatabase.getFolderList(self,PatientDirs[x])[0].values()
    else: ExtractionDirs.append(PatientDirs[x])

    # Load and Extract features for each selected folder
    for index in xrange(radiomicsDatabase.lenghtList(ExtractionDirs)):
      for settings in fileIdentifierSettings:
        print(patientName, ExtractionDirs[index])
        ImageFilePath, LabelFilePath = radiomicsDatabase.getDataFiles(ExtractionDirs[index],includeSubfolders,settings["Mask"],settings["selImage"],settings["selLabel"])
        if ImageFilePath:# and LabelFilePath:
          # Load Image Nodes into Slicer
          imageNode, labelNode = radiomicsDatabase.loadDataSlicer(self,ImageFilePath,LabelFilePath,printfile)
          #use binarizeLabelMapToValue
          createLabelMap(self,imageNode, labelNode, outputdir, IDcurrPatient)
        else: print("could not find image or label path: " + patientName, file=printfile)
      radiomicsDatabase.deleteDataSlicer(self)
      slicer.mrmlScene.Clear(0)
    radiomicsDatabase.deleteDataSlicer(self)
    slicer.mrmlScene.Clear(0)
  printfile.close()


def reversedim(M,k=0):
    idx = tuple((slice(None,None,-1) if ii == k else slice(None) 
            for ii in xrange(M.ndim)))
    return M[idx]
    

def binarizeLabelMapToValue(labelNode, labelValue=1):
  labelNodeImageData = labelNode.GetImageData()
  change = slicer.vtkImageLabelChange()
  change.SetInputData(labelNodeImageData)
  change.SetOutput(labelNodeImageData)
  change.SetOutputLabel(labelValue)
  
  for i in xrange(1,int(labelNodeImageData.GetScalarRange()[1])+1):
    change.SetInputLabel(i)
    change.Update()
    
  labelNode.SetAndObserveImageData(labelNodeImageData)
  return labelNode


def createLabelMap(self, dataNode, labelNode, outputDir, IDcurrPatient):
  """
  self.sliceXarray = numpy.rollaxis(self.sliceXarray,1)[:,:,None] #512,36,1
  #self.sliceXarray = self.sliceXarray[:,:,None]
  
  self.sliceYarray = numpy.rollaxis(self.sliceYarray,1)[:,:,None] #512,36,1
  #self.sliceYarray = self.sliceYarray[:,:,None]
  
  #self.slizeZarray = numpy.rot90(self.sliceZarray)
  self.sliceZarray = self.sliceZarray[:,:,None] #512,512,1
  
  self.sliceXnode = slicer.vtkMRMLScalarVolumeNode()
  self.sliceYnode = slicer.vtkMRMLScalarVolumeNode()
  self.sliceZnode = slicer.vtkMRMLScalarVolumeNode()
  self.sliceXnode.SetName('SliceX')
  self.sliceYnode.SetName('SliceY')
  self.sliceZnode.SetName('SliceZ')
   
  self.sliceXNodeDisplayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
  slicer.mrmlScene.AddNode(self.sliceXNodeDisplayNode)
  self.sliceXnode.SetAndObserveDisplayNodeID(self.sliceXNodeDisplayNode.GetID())
  
  self.sliceYNodeDisplayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
  slicer.mrmlScene.AddNode(self.sliceYNodeDisplayNode)
  self.sliceYnode.SetAndObserveDisplayNodeID(self.sliceYNodeDisplayNode.GetID())

  self.sliceZNodeDisplayNode = slicer.vtkMRMLVectorVolumeDisplayNode()
  slicer.mrmlScene.AddNode(self.sliceZNodeDisplayNode)
  self.sliceZnode.SetAndObserveDisplayNodeID(self.sliceZNodeDisplayNode.GetID())
  """
  imageFilePath = dataNode.GetStorageNode().GetFileName()
  imageName = os.path.basename(imageFilePath).replace('.nrrd','')
  
  reconDir = os.path.dirname(imageFilePath)
  studyDir = os.path.dirname(reconDir)
  segDir  = [dirpath for dirpath in glob.glob(os.path.join(studyDir,'*')) if 'Segmentations' in dirpath][0]
  resourcesDir = [dirpath for dirpath in glob.glob(os.path.join(studyDir,'*')) if 'Resources' in dirpath][0]
  spacing = dataNode.GetSpacing()
  origin = dataNode.GetOrigin()
  #pdb.set_trace()
  
  arrays = []
  for r,d,f in os.walk(studyDir):
    [arrays.append(os.path.join(r,file)) for file in fnmatch.filter(f, '*.npy')]

  try:
    name = os.path.basename(arrays[0]).replace('.npy', '')
  except IndexError:
    print(IDcurrPatient, ': FAILED TO PROCESS NPY FILE')
    return
  arr = numpy.load(arrays[0])
  #arr = numpy.ascontiguousarray(arr)
  
  #nump_arr = reversedim(arr,0)
  nump_arr = numpy.swapaxes(arr, 0, 2)
  
  #nump_arr = nump_arr[...,::-1]
  #nump_arr = numpy.rollaxis(numpy.rollaxis(nump_arr,2),2,1)

  self.labelMapnode = slicer.vtkMRMLScalarVolumeNode()
  self.labelMapnode.SetName('labelMap')
  self.labelMapnode.LabelMapOn()
  
  self.labelMapnodeDisplayNode = slicer.vtkMRMLScalarVolumeDisplayNode()
  slicer.mrmlScene.AddNode(self.labelMapnodeDisplayNode)
  self.labelMapnode.SetAndObserveDisplayNodeID(self.labelMapnodeDisplayNode.GetID())
  self.labelMapnodeDisplayNode.SetAndObserveColorNodeID('vtkMRMLColorTableNodeFileGenericColors.txt')
  
  try:
    self.labelMapnode = renderArray(self, nump_arr, self.labelMapnode, dataNode, shape=nump_arr.shape, spacing=spacing, origin=origin)
  except ValueError:
    print(IDcurrPatient, ': FAILED TO CONVERT TO LABEL MAP')
    return
  #self.sliceXnode = self.renderSlice(self.sliceXarray, self.sliceXnode, self.dataNode, shape=self.sliceXarray.shape, spacing=(x,z,1))
  #self.sliceYnode = self.renderSlice(self.sliceYarray, self.sliceYnode, self.dataNode, shape=self.sliceYarray.shape, spacing=(y,z,1))
  #self.sliceZnode = self.renderSlice(self.sliceZarray, self.sliceZnode, self.dataNode, shape=self.sliceZarray.shape, spacing=(x,y,1))
  
  self.labelMapnode = binarizeLabelMapToValue(self.labelMapnode)  
  self.labelMapnodeDisplayNode.SetInputImageDataConnection(self.labelMapnode.GetImageDataConnection())
  self.labelMapnodeDisplayNode.UpdateImageDataPipeline()
  
  volumesLogic = slicer.vtkSlicerVolumesLogic()
  volumesLogic.CenterVolume(dataNode)
  volumesLogic.CenterVolume(self.labelMapnode)
  
  labelMapNodeFileName = os.path.join(segDir, imageName + '_labelMap.nrrd')
  saveLabelMap = slicer.util.saveNode(self.labelMapnode, labelMapNodeFileName, properties={"filetype": ".nrrd"})
  #saveNode = slicer.util.saveNode(dataNode, imageFilePath, properties={"filetype": ".nrrd"})
  arraysName = os.path.basename(arrays[0])
  shutil.move(arrays[0],os.path.join(resourcesDir,arraysName))
  
  labelMapNodeSITK = sitk.ReadImage(str(labelMapNodeFileName))
  FlipZAxis = sitk.FlipImageFilter()
  FlipZAxis.SetDebug(False)
  FlipZAxis.SetFlipAxes([False, False, True])
  FlipZAxis.SetFlipAboutOrigin(True)
  FlipZAxis.SetNumberOfThreads(4)
  labelMapNodeSITK = FlipZAxis.Execute(labelMapNodeSITK)
  FlipZAxis.Execute(labelMapNodeSITK)
  sitk.WriteImage(labelMapNodeSITK, str(labelMapNodeFileName) )
  """
  sliceXfilename = os.path.join(outputDir, 'test_sliceX.tiff')
  savex = slicer.util.saveNode(self.sliceXnode, sliceXfilename, properties={"filetype": ".tiff"})
  
  #sliceYfilename = os.path.join(outputDir, 'test_sliceY.tiff')
  #savey = slicer.util.saveNode(self.sliceYnode, sliceYfilename, properties={"filetype": ".tiff"})
  
  #sliceZfilename = os.path.join(outputDir, 'test_sliceZ.tiff')
  #savez = slicer.util.saveNode(self.sliceZnode, sliceZfilename, properties={"filetype": ".tiff"})
  """
  
def renderArray(self, labelNodeArray, labelNode, imageNode, shape=(512,512,88), spacing=(1,1,1), origin=(0,0,0)):
  ras2ijk = vtk.vtkMatrix4x4()
  ijk2ras = vtk.vtkMatrix4x4()
  imageNode.GetRASToIJKMatrix(ras2ijk)
  imageNode.GetIJKToRASMatrix(ijk2ras)
  labelNode.SetRASToIJKMatrix(ras2ijk)
  labelNode.SetIJKToRASMatrix(ijk2ras)
  
  labelNodeImageData = vtk.vtkImageData()
  labelNodeImageData.DeepCopy(imageNode.GetImageData())
  #labelNodeImageData.AllocateScalars(4,1)
  #labelNodeImageData.SetDimensions(shape)
  labelNodePointData = labelNodeImageData.GetPointData()

  """
  # Numpy array is converted from signed int16 to signed vtkShortArray
  scalarArray = vtk.vtkShortArray()
  dims1D = labelNodeArray.size #labelNodePointData.GetScalars().GetSize()
  flatArray = labelNodeArray.reshape(dims1D, order='C')
  scalarArray = vtk.util.numpy_support.numpy_to_vtk(flatArray)
  """
  scalarArray = vtk.vtkShortArray()
  dims1D = labelNodePointData.GetScalars().GetSize() #labelNodePointData.GetScalars().GetSize()
  flatArray = labelNodeArray.reshape(dims1D, order='F')
  scalarArray = vtk.util.numpy_support.numpy_to_vtk(flatArray) # VTK Unsigned Char Array =3, short =4, uint = 7
     
  labelNodePointData.SetScalars(scalarArray)
  labelNodeImageData.Modified()
  
  slicer.mrmlScene.AddNode(labelNode)
  labelNode.SetAndObserveImageData(labelNodeImageData)
  labelNode.SetSpacing(spacing)
  labelNode.SetOrigin(origin)
     
  return labelNode

def renderSlice(self, sliceNodeArray, sliceNode, imageNode, shape=(512,512,88), spacing=(1,1,1), origin=(0,0,0)):
  # Initializes a vtkMRMLScalarVolumeNode for the SegmentCAD Output and copies ijkToRAS matrix and Image data from nodeLabel
  """
  ras2ijk = vtk.vtkMatrix4x4()
  ijk2ras = vtk.vtkMatrix4x4()
  imageNode.GetRASToIJKMatrix(ras2ijk)
  imageNode.GetIJKToRASMatrix(ijk2ras)
  sliceNode.SetRASToIJKMatrix(ras2ijk)
  sliceNode.SetIJKToRASMatrix(ijk2ras)
  """
  
  sliceNodeImageData = vtk.vtkImageData()
  sliceNodeImageData.AllocateScalars(4,1)
  sliceNodeImageData.SetDimensions(shape)

  sliceNodePointData = sliceNodeImageData.GetPointData()
  
  """
  # Numpy array is converted from signed int16 to signed vtkShortArray
  scalarArray = vtk.vtkShortArray()
  dims1D = sliceNodeArray.size #sliceNodePointData.GetScalars().GetSize()
  flatArray = sliceNodeArray.reshape(dims1D, order='C')
  scalarArray = vtk.util.numpy_support.numpy_to_vtk(flatArray)
  """
  
  dims1D = sliceNodeArray.size #sliceNodePointData.GetScalars().GetSize()
  flatArray = sliceNodeArray.reshape(dims1D, order='C')
  scalarArray = vtk.util.numpy_support.numpy_to_vtk(flatArray, array_type=4) # VTK Unsigned Char Array =3, short =4, uint = 7
     
  sliceNodePointData.SetScalars(scalarArray)
  sliceNodeImageData.Modified()
  
  slicer.mrmlScene.AddNode(sliceNode)
  sliceNode.SetAndObserveImageData(sliceNodeImageData)
  sliceNode.SetSpacing(spacing)
  sliceNode.SetOrigin(origin)
     
  return sliceNode
  
  """
  # Corresponding display node and color table nodes created for SegmentCAD label Output
  self.SegmentCADLabelMapDisplay = slicer.vtkMRMLLabelMapVolumeDisplayNode()
  self.SegmentCADLabelMapDisplay.SetScene(slicer.mrmlScene)
  self.SegmentCADLabelMapDisplay.SetAndObserveColorNodeID('vtkMRMLColorTableNodeFileGenericColors.txt')
  
  if vtk.VTK_MAJOR_VERSION <= 5:
    self.SegmentCADLabelMapDisplay.SetInputImageData(self.SegmentCADLabelMap.GetImageData())
  else:
    self.SegmentCADLabelMapDisplay.SetInputImageDataConnection(self.SegmentCADLabelMap.GetImageDataConnection())
  self.SegmentCADLabelMapDisplay.UpdateImageDataPipeline()
  
  slicer.mrmlScene.AddNode(self.SegmentCADLabelMapDisplay)
  self.SegmentCADLabelMap.SetAndObserveDisplayNodeID(self.SegmentCADLabelMapDisplay.GetID())
  self.SegmentCADLabelMapDisplay.UpdateScene(slicer.mrmlScene)
  """

  
def createNumpyArray (self, imageNode):
  # Generate Numpy Array from vtkMRMLScalarVolumeNode
  imageData = vtk.vtkImageData()
  imageData = imageNode.GetImageData()
  shapeData = list(imageData.GetDimensions())
  shapeData.reverse()
  return (vtk.util.numpy_support.vtk_to_numpy(imageData.GetPointData().GetScalars()).reshape(shapeData))

def tumorVoxelsAndCoordinates(self, arrayROI, arrayDataNode):
  coordinates = numpy.where(arrayROI != 0) # can define specific label values to target or avoid
  values = arrayDataNode[coordinates].astype('int64')
  return(values, coordinates)
  
def paddedTumorMatrixAndCoordinates(self, shape, targetVoxels, targetVoxelsCoordinates):
  matrix = numpy.empty(shape, dtype='float64')
  matrix[:] = numpy.NAN
  matrix[targetVoxelsCoordinates] = targetVoxels
  return(matrix, targetVoxelsCoordinates)
  
def padMatrix(self, a, matrixCoordinates, dims, voxelArray):
  # pads matrix 'a' with zeros and resizes 'a' to a cube with dimensions increased to the next greatest power of 2
  # numpy version 1.7 has numpy.pad function
       
  # center coordinates onto padded matrix  # consider padding with NaN or eps = numpy.spacing(1)
  pad = tuple(map(operator.div, tuple(map(operator.sub, dims, a.shape)), ([2,2,2])))
  matrixCoordinatesPadded = tuple(map(operator.add, matrixCoordinates, pad))
  matrix2 = numpy.zeros(dims)
  matrix2[matrixCoordinatesPadded] = voxelArray
  return (matrix2, matrixCoordinatesPadded)
