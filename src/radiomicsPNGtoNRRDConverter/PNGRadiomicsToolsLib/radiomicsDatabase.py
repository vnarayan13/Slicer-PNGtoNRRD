from __future__ import print_function
import numpy as np
import string
import pdb
import os, slicer

#   pdb.set_trace() # Set breakpoint (c: continue, s: step, n: next line)
#   dir() lists all attributes


def deleteDataSlicer(self):
    slicer.mrmlScene.Clear(0)
    self.imageNodes = {}
    self.labelNodes = {}
    self.ModelNodes = {}


def loadDataSlicer(self,ImageFile,LabelFile,printfile):
    """ loads Image and Label into Slicer
    """
    Ima = list(slicer.util.loadVolume(ImageFile,returnNode=True))
    if not (Ima[0]==True): print("Error loading Image data",file=printfile)
    else:
        print("Image file loaded " + str(ImageFile),file=printfile)
        Ima = Ima[1]
    Label = list(slicer.util.loadVolume(LabelFile,returnNode=True))
    if not (Label[0]==True): print("Error loading Label data",file=printfile)
    else:
        print("Label file loaded " + str(LabelFile),file=printfile)
        Label = Label[1]
        Label.LabelMapOn()
        
    return Ima, Label

    
def loadDataIntoSlicer(self,selectedDir):
    """ loads data from directory into slicer: now load scene file
    """
    files = os.listdir(selectedDir)
    Labels = Images = {}
    for y in range(0,len(files)):
        if files[y].find("nrrd") > 0:
            if files[y].find("label") > 0:
                properties = {}
                properties['labelmap'] = True
                tempNode = list(slicer.util.loadVolume(os.path.join(selectedDir, files[y]),properties,returnNode=True))[1]
                tempNode.SetName(files[y])
                Labels[len(Labels)] = tempNode
            else:
                tempNode = list(slicer.util.loadVolume(os.path.join(selectedDir, files[y]),returnNode=True))[1]
                tempNode.SetName(files[y])
                Images[len(Images)] = tempNode
    self.imageNodes = Images # Be carefull: only latest data is in the node list
    self.labelNodes = Labels
    

def getFolderList(self,selectedDir,excludeDirName=False):
    if not selectedDir: return False, {}
    patientDirs  = patientNames = {}
    # Get all main directories within selectedDir
    patientNames = [ name for name in os.listdir(selectedDir) if os.path.isdir(os.path.join(selectedDir, name)) ]
    # Remove OutputDirName from list
    if excludeDirName in patientNames: del patientNames[patientNames.index(excludeDirName)] 
    # Generate Dir list
    for index, dirname in enumerate(patientNames): patientDirs[index] = os.path.join(selectedDir, dirname)
    
    return patientDirs, patientNames


def getDataFiles(selectedDir,SubFolders=False,Mask=False,selImage=False,selLabel='label'):
    """ Select two data files: one image and one label
    """
    if not selectedDir: return False
    import os, os.path, path, fnmatch
    
    # Gives all files masked and within subfolders
    dataFilePaths = []
    for root, dirs, filenames in os.walk(selectedDir):
        [dataFilePaths.append(str(os.path.join(root,file))) for file in fnmatch.filter(filenames, Mask)]#files if file.endswith(Mask.strip("*"))]
    #files = getFileList(selectedDir,SubFolders,Mask)  
    
    # Select label file with selLabel
    LabelFilePath = []
    for filePath in dataFilePaths:
        fileName = str(os.path.basename(filePath))
        if all(testString(fileName,selLabel)): LabelFilePath = filePath
    
    # Select image file with selImage
    ImageFilePath = []
    if selImage: #is not False:
        for filePath in dataFilePaths:         
            if filePath is not LabelFilePath:
                fileName = str(os.path.basename(filePath))
                if all(testString(fileName,selImage)): ImageFilePath = filePath
    else: # Only one image file is present per folder (NOT label name)
        for filePath in dataFilePaths:
            fileName = str(os.path.basename(filePath))
            if selLabel not in fileName: ImageFilePath = filePath #bug: can store ALL other files
    
    return ImageFilePath, LabelFilePath


def testString(String,Conditions):
    String = String.upper()
    Result = [False]
    if lenghtList(Conditions[0])==1:
        condition = Conditions[0][0]
        if (condition in String) and (not any(substring.upper() in String for substring in Conditions[1])):
            Result = [True] #[True,True]
    else:    
        if all(substring.upper() in String for substring in Conditions[0]) and (not any(substring.upper() in String for substring in Conditions[1])):  
            Result = [True]
    return Result


def lenghtList(List):
    if isinstance(List, list): length = len(List)
    else: length = 1
    return length


def getFileList(selectedDir,SubFolders=False,Mask='*'):
    """ Gives all files back with Directory. Can be maksed with Mask
        e.g. Mask = '*.dcm" gives all dicom files

        os.path.dirname(os.path.realpath(file)) gives directory of file 
    """ 
    from path import path
    
    if Mask is False: Mask='*'
    selDir = path(selectedDir)
    if SubFolders:    
        # Get all files with subdir
        files = []
        for file in selDir.walkfiles(Mask): files.append(os.path.abspath(file))
    else:
        # Get all files in current dir
        files = selDir.files(Mask)
    
    return files


def getIDcurrPatient(self,selector,Input=False):
    """ Get ID for current patient: currently from directory name where image file is stored
        1 = From Image file in the image node
        2 = From the Directory in Input (Input is root patient dir)
    """
    PatientID = []
    if selector == 1:
        if self.selImageNode:
            imageFileName = self.selImageNode.GetStorageNode().GetFileName()
            if imageFileName:
                a = []      
                for n in xrange(len(imageFileName)):
                    if imageFileName.find(os.sep, n) == n: a.append(n)
                PatientID = imageFileName[a[len(a)-2]+1:max(a)]
    if selector == 2:
        if Input: 
            PatientID = os.path.basename(Input)
    return PatientID
    

def saveDatabase(PatientID,Results,file):
    import csv, datetime
    if not os.path.isfile(file): open(file,mode='w') # First time open the file
    reader = csv.reader(open(file,mode='r+'))
    if not reader: return
    
    table = [[e for e in r] for r in reader]

    curr_time = datetime.datetime.now()
    DateTime = str(curr_time.year) + '-' + str(curr_time.month) + '-' + str(curr_time.day) + '_' + str(curr_time.hour) + ':' + str(curr_time.minute) 

    writer = csv.writer(open(file,mode='a'),lineterminator='\n')      
    if not table: # First entry
        writer.writerow(['PatientID'] + ['DateTime'] + Results.keys()) # Write headers
        writer.writerow([PatientID] + [DateTime] + Results.values())
    else:         # Replace or Append
        writer.writerow([PatientID] + [DateTime] + Results.values())            


def initializeDatabase(self):
    """ Initialize Database file: Set self.datafile and remove if clear and existing
    """
    if self.para2.checked: # If Matlab feature extraction
        self.datafile = os.path.join(self.outputDir,'MatlabFeatures.csv')       
    else:    # If Python feature extraction
        self.datafile = os.path.join(self.outputDir,self.datafileName)
    if self.para3.checked and os.path.isfile(self.datafile): os.remove(self.datafile)                


def readDatabase(self, file):
    """ Read data from file: error messages: 1= no file found, 2= file found but corrupt, 3= file found but no data
    """
    import csv
    if not file: return False, 1
    if not os.path.isfile(file): return False, 1
    reader = csv.reader(open(file,mode='r+'))
    if not reader: return False, 2
    table = [[e for e in r] for r in reader]
    if len(table) < 2: return False, 3
    
    # Generate larger string matrix that matches input file
    temp = np.chararray((len(table),len(table[0])),itemsize=100)
    for index,name in enumerate(table[0]):  # for each header (column)
        for k in range(0,len(table)): # for each patient (row)
            temp[k,index] = table[k][index]                

    # Convert in lists of data (call as: name['Max'][1])
    StartColFloat = 2
    for index,feat in enumerate(temp[0,:]): 
        if index < StartColFloat: # read these columns as lists of strings  
            self.radiomicsBatch[feat] = temp[1:,temp[0,:] == feat]  
        else:       # Load these columns as float data
            dat = temp[1:,temp[0,:] == feat]
            self.radiomicsBatch[feat] = map(float, dat[:,0])

    return True, 0


def loadDatabase(self, file):
    
    loaded, message = readDatabase(self, file)
    if loaded:
      matched, onlyImaging, onlyRadiomics = CompareRadiomicsWithPatientDirs(self)
      if  not onlyImaging and not onlyRadiomics: self.statusBar.text = str(len(matched)) + " Matched Imaging + Radiomics"
      if  onlyImaging and not onlyRadiomics:     self.statusBar.text = str(len(matched)) + " Matched Imaging + Radiomics ( " + str(len(onlyImaging)) + "only Imaging)"
      if  not onlyImaging and onlyRadiomics:     self.statusBar.text = str(len(matched)) + " Matched Imaging + Radiomics ( " + str(len(onlyRadiomics)) + "only Radiomics)"
    else:
      self.statusBar.text = 'no radiomics data'
    

def CompareRadiomicsWithPatientDirs(self):
    """ Compare loaded Radiomics Data with Patients in input Directory (return patientsIDs that are Matched, Only Folder, Only Radiomics 
    """
    # Get list of all patients in folder
    patientNames, patientDirs = getPatientList(self,self.mainPatientdir,self.outputDir)
    # Compare with loaded patient data
    matched = onlyFolder = onlyRadiomics = {} 
    if self.radiomicsBatch:
        temp = self.radiomicsBatch['PatientID'].tolist()
        patientIDindata = {}
        for i in xrange(len(temp)): patientIDindata[i] = temp[i][0]

        matched = set(patientNames.values()) & set(patientIDindata.values())     
        onlyFolder = set(patientNames.values()) - matched
        onlyRadiomics = set(patientIDindata.values()) - matched

    return matched, onlyFolder, onlyRadiomics


def statsFeatures(self,featuresToPlot):
    nCurrData  = nBatchData = {}

    if self.radiomicsCurr:    
      for index,feat in enumerate(featuresToPlot): 
        nBatchData[index] = (self.radiomicsBatch[feat] - np.mean(self.radiomicsBatch[feat]))/np.std(self.radiomicsBatch[feat])
        nCurrData[index]  = (self.radiomicsCurr[feat] - np.mean(self.radiomicsBatch[feat]))/np.std(self.radiomicsBatch[feat])
    elif self.radiomicsBatch:
      for index,feat in enumerate(featuresToPlot):
        nBatchData[index] = (self.radiomicsBatch[feat] - np.mean(self.radiomicsBatch[feat]))/np.std(self.radiomicsBatch[feat])

    return nCurrData, nBatchData


def statsAsCSV(self):
    """ print comma separated value file with header keys in quotes
    """
    csv = ""
    header = ""
    for k in self.keys[:-1]:
        header += "\"%s\"" % k + ","
    header += "\"%s\"" % self.keys[-1] + "\n"
    csv = header
    for i in self.labelStats["Labels"]:
        line = ""
        for k in self.keys[:-1]:
            line += str(self.labelStats[i,k]) + ","
        line += str(self.labelStats[i,self.keys[-1]]) + "\n"
        csv += line
    return csv

 
def saveStats(self,fileName):
    fp = open(fileName, "w")
    fp.write(self.statsAsCSV())
    fp.close()


