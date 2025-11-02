import imageio
import numpy as np
import time
def imageBreak(image,iconDim,impos):
    im=np.array(imageio.imread(image))
    subdiv={
        'x':len(im)//iconDim['x'],
        'y':len(im)//iconDim['y']
    }
    nims=[]
    for i in range(subdiv['x']):
        for j in range(subdiv['y']):
            nims.append({'im':im[i*iconDim['x']:(i+1)*iconDim['x'],j*iconDim['y']:(j+1)*iconDim['y']],'pos':{'x':impos['x']+i*iconDim['x'],'y':impos['y']+j*iconDim['y']}})
    return nims
    
