import numpy
import os
import fnmatch
import scipy
import scipy.misc

dir = 'C:\\Users\\Vivek Narayan\\Desktop\\VIVEK MASKS\\Tumor'
#outdir = os.path.join(os.path.dirname(dir),'Mask_Arrays')

pngs = []
for r,d,f in os.walk(dir):
  [pngs.append(os.path.join(r,file)) for file in fnmatch.filter(f, '*.png')]
  
for png in pngs:
  arr = scipy.misc.imread(png)
  try:
    narr = arr.reshape((arr.shape[0]/512.0, 512, 512))
  except ValueError:
    print png
  path = png.replace('.png', '')
  numpy.save(path,narr)
  
arrays = []
for r,d,f in os.walk(dir):
  [arrays.append(os.path.join(r,file)) for file in fnmatch.filter(f, '*.npy')]

for array in arrays:
    nump_arr = numpy.load(array)
    

 #553290_NC