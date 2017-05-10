from __main__ import vtk, qt, ctk, slicer, os, datetime
import string
import pdb
import PNGRadiomicsToolsLib

class radiomicsPNGtoNRRDConverter:
  def __init__(self, parent):  
    parent.title = "RadiomicsPNGtoNRRDConverter"
    parent.categories = ["Radiomics"]
    parent.contributors = ["Vivek Narayan / Hugo Aerts"]
    parent.helpText = """
    Use this module to help convert PNG label maps to NRRD label maps (requires preprocessing of PNGs to numpy arrays)
    """
    parent.acknowledgementText = """
    """ 
    self.parent = parent

#
# Widget
#

class radiomicsPNGtoNRRDConverterWidget:
  def __init__(self, parent=None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

    self.inputPatientdir = self.outputPatientdir = {}
    
  def setup(self):

    # intialize variables
    # Data of current loaded patient
    self.IDcurrPatient = {}
    self.imageNodes = {}      # List of currently loaded image nodes
    self.labelNodes = {}      # List of currently loaded label nodes
    self.ModelNodes = {}
    # Data of database
    self.mainPatientdir = self.outputDir = self.datafile = {}

    #---------------------------------------------------------
    # 2D Slice Snapshots
    self.PNGConverterCollapsibleButton = ctk.ctkCollapsibleButton()
    self.PNGConverterCollapsibleButton.text = "PNG Converter"
    self.layout.addWidget(self.PNGConverterCollapsibleButton)
    self.PNGConverterCollapsibleButton.collapsed = False
    self.PNGConverterFormLayout = qt.QFormLayout(self.PNGConverterCollapsibleButton)
    """
    # Input 1: Input Image
    self.input4Frame = qt.QFrame(self.PNGConverterCollapsibleButton)
    self.input4Frame.setLayout(qt.QHBoxLayout())
    self.PNGConverterFormLayout.addWidget(self.input4Frame)
    
    self.input4Selector = qt.QLabel("Input Image: ", self.input4Frame)
    self.input4Frame.layout().addWidget(self.input4Selector)
    self.input4Selector = slicer.qMRMLNodeComboBox(self.input4Frame)
    self.input4Selector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.input4Selector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.input4Selector.addEnabled = False
    self.input4Selector.removeEnabled = False
    self.input4Selector.setMRMLScene( slicer.mrmlScene )
    self.input4Frame.layout().addWidget(self.input4Selector)

    # Input 2: Input Segmentation
    self.input5Frame = qt.QFrame(self.PNGConverterCollapsibleButton)
    self.input5Frame.setLayout(qt.QHBoxLayout())
    self.PNGConverterFormLayout.addWidget(self.input5Frame)
    
    self.input5Selector = qt.QLabel("Input Label:  ", self.input5Frame)
    self.input5Frame.layout().addWidget(self.input5Selector)
    self.input5Selector = slicer.qMRMLNodeComboBox(self.input5Frame)
    self.input5Selector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.input5Selector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 1 )
    self.input5Selector.addEnabled = False
    self.input5Selector.removeEnabled = False
    self.input5Selector.setMRMLScene( slicer.mrmlScene )
    self.input5Frame.layout().addWidget(self.input5Selector)
    """
    # Input 1: Input Directory selector
    self.input6Frame = qt.QFrame(self.PNGConverterCollapsibleButton)
    self.input6Frame.setLayout(qt.QHBoxLayout())
    self.PNGConverterFormLayout.addWidget(self.input6Frame)
    
    self.input6Selector = qt.QLabel("Input Directory (DICOM):  ", self.input6Frame)
    self.input6Frame.layout().addWidget(self.input6Selector)
    self.input6Button = qt.QPushButton("Select main directory DICOM files")
    self.input6Button.toolTip = "Select main directory with DICOM files (folder names are patient names)"
    self.input6Button.enabled = True
    self.input6Frame.layout().addWidget(self.input6Button)

    # Input 2: Output Directory selector
    self.input7Frame = qt.QFrame(self.PNGConverterCollapsibleButton)
    self.input7Frame.setLayout(qt.QHBoxLayout())
    self.PNGConverterFormLayout.addWidget(self.input7Frame)
    
    self.input7Selector = qt.QLabel("Output Directory:  ", self.input7Frame)
    self.input7Frame.layout().addWidget(self.input7Selector)
    self.input7Button = qt.QPushButton("Select main directory output NRRD or NFITI files")
    self.input7Button.toolTip = "Select main directory for output NRRD or NIFTI files (folder names are patient names)"
    self.input7Button.enabled = True
    self.input7Frame.layout().addWidget(self.input7Button)
    
    # PNG Slice Extract Button
    self.PNGConverterButton = qt.QPushButton("Convert To NRRD")
    self.PNGConverterFormLayout.addWidget(self.PNGConverterButton)
    #---------------------------------------------------------
    
    # Apply Screenshot button
    self.applyScreenButton = qt.QPushButton("Extract Pictures current view")
    self.applyScreenButton.toolTip = "Extract the model from the current 3D view" 
    self.parent.layout().addWidget(self.applyScreenButton)

    # Connections
    self.input6Button.connect('clicked(bool)', self.onInput6Button)
    self.input7Button.connect('clicked(bool)', self.onInput7Button)

    self.PNGConverterButton.connect('clicked(bool)', self.onPNGConverter)
  
  def onInput6Button(self):
    self.inputPatientdirPNG = qt.QFileDialog.getExistingDirectory()
    self.input6Button.text = self.inputPatientdirPNG

  def onInput7Button(self):
    self.outputPatientdirPNG = qt.QFileDialog.getExistingDirectory()
    self.input7Button.text = self.outputPatientdirPNG
    
  def onPNGConverter(self):
    fileIdentifierSettings = []
    
    CTSCAN = {}
    CTSCAN["Mask"] = "*.nrrd"
    CTSCAN["selImage"] = [[""] ,["npy","label"]]
    CTSCAN["selLabel"] = [[""],["nrrd"]]
    CTSCAN["levels"] = False
    fileIdentifierSettings.append(CTSCAN)
    """
    CTSCAN = {}
    CTSCAN["Mask"] = "*.nrrd"
    CTSCAN["selImage"] = [[] ,["bone", "label", "tissue"]]
    CTSCAN["selLabel"] = [["label"],["bone"]]
    CTSCAN["levels"] = False
    fileIdentifierSettings.append(CTSCAN)
    """
    """
    CTSCAN = {}
    CTSCAN["Mask"] = "*.nrrd"
    CTSCAN["selImage"] = [[] ,["bone", "label", "tissue"]]
    CTSCAN["selLabel"] = [["tissue"],["bone"]]
    CTSCAN["levels"] = False
    fileIdentifierSettings.append(CTSCAN)
    """
    """
    BiasFieldCorrected_AXIAL_T1 = {}
    BiasFieldCorrected_AXIAL_T1["Mask"] = "*.nii.gz"
    BiasFieldCorrected_AXIAL_T1["selImage"] = [["Bias","T1"] ,["Flair","T2"]]
    BiasFieldCorrected_AXIAL_T1["selLabel"] = [["T1", "FSL"],["Flair", "T2"]]
    BiasFieldCorrected_AXIAL_T1["levels"] = [1]
    fileIdentifierSettings.append(BiasFieldCorrected_AXIAL_T1)
    """
    """
    lowres = {}
    lowres["Mask"] = "*.nrrd"
    lowres["selImage"] = [["T1"] ,["Cavity", "Label"]]
    lowres["selLabel"] = [["Label"],["Post","Resampled"]]
    lowres["levels"] = False
    fileIdentifierSettings.append(lowres)
    """
    
    #if not(self.selImageNode) or not(self.selLabelNode):
      #qt.QMessageBox.critical(slicer.util.mainWindow(),'Error', 'Select a valid Image and Segmentation Label Map')
      #return
    
    PNGRadiomicsToolsLib.pngConverter.Execute(self, self.inputPatientdirPNG, self.outputPatientdirPNG, fileIdentifierSettings, self.PNGConverterButton)