import os
import fnmatch
import glob
import shutil
import re
import pdb

dirin = "Z:\\DATA\\Lung\\NLST\\2_SlicerData\\CC1"
pngDir = "E:\\Users\\cp587\\Desktop\\Nodule_PNG"

hierarchyDict = {}
dirs = glob.glob(os.path.join(dirin,'*'))
for ind, patient in enumerate(dirs):
  patientID = os.path.basename(patient)
  studydates = glob.glob(os.path.join(patient,'*'))
  hierarchyDict[patient] = {}
  for study in studydates:
    hierarchyDict[patient][study] = {}
    studydatename = os.path.basename(study)
    subfolders = [dirpath for dirpath in glob.glob(os.path.join(study,'*')) if os.path.isdir(dirpath)]    
    prefix = '_'.join(os.path.basename(subfolders[0]).split('_')[:-1])
    suffix = "_Segmentations"
    segmentationsDir = os.path.join(study,prefix+suffix)
    if not os.path.exists(segmentationsDir):
      os.makedirs(segmentationsDir)
    for subfolder in subfolders:
      hierarchyDict[patient][study][subfolder] = []    

npyArrays = []
for root, dir, fp in os.walk(pngDir):
  [npyArrays.append(os.path.join(root,file)) for file in fnmatch.filter(fp,'*.npy')]
 
for npy in npyArrays:
  print npy
  try:
    pid = os.path.basename(npy).split('.s1.')[0]
    studydate = (os.path.basename(npy).split('.s1.')[1]).split('-')[0]
  except IndexError:
    try:
      pid = os.path.basename(npy).split('.s2.')[0]
      studydate = (os.path.basename(npy).split('.s2.')[1]).split('-')[0]
    except IndexError:
      pid = os.path.basename(npy).split('.s3.')[0]
      studydate = (os.path.basename(npy).split('.s3.')[1]).split('-')[0]
  
  for patient in hierarchyDict:
    if pid in os.path.basename(patient):
      for study in hierarchyDict[patient]:
        if studydate in os.path.basename(study):
          for subfolder in hierarchyDict[patient][study]:
            if 'Segmentations' in os.path.basename(subfolder):
              outfile = os.path.join(subfolder,os.path.basename(npy))
              print npy
              print outfile
              pdb.set_trace()
              #shutil.copy(npy,outfile)




	   