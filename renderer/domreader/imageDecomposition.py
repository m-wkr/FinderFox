import imageio
import numpy as np
import time
import math
def imageBreak(image,imageDim,iconDim,impos):
    im=np.array(imageio.v2.imread(image))
    scale={
        'x':im.shape[0]/imageDim['x'],
        'y':im.shape[1]/imageDim['y']
    }
    subdiv={
        'x':imageDim['x']/iconDim['x'],
        'y':imageDim['y']/iconDim['y']
    }
    nims=[]
    if subdiv['x']>4:
        scale['x']=scale['x']*subdiv['x']/4
        subdiv['x']=4
    if subdiv['y']>4:
        scale['y']=scale['y']*subdiv['y']/4
        subdiv['y']=4
    for i in range(math.floor(subdiv['x'])):
        for j in range(math.floor(subdiv['y'])):
            nims.append({'im':im[math.floor(i*scale['x']*iconDim['x']):math.floor((i+1)*scale['x']*iconDim['x']),math.floor(j*scale['y']*iconDim['y']):math.floor((j+1)*scale['y']*iconDim['y'])],'pos':{'x':math.floor(impos['x']+i*iconDim['x']),'y':math.floor(impos['y']+j*iconDim['y'])}})
    return nims
    
# nims=imageBreak(input('url here: '),{'x':1600,'y':1600},{'x':16,'y':16},{'x':0,'y':0})
# for nim in nims:
#     imageio.v2.imwrite('C:/Users/sam05/OneDrive/Desktop/CODE/CamHack-/renderer/domreader/'+str(nim['pos']['x'])+'-'+str(nim['pos']['y'])+'.png',nim['im'])