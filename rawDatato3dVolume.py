import numpy as np
import sys,struct
from math import atan2, pi, hypot,floor,ceil
from  fileSpesification_DataFinder import *


def volumeFinder(raw,probAxissizeX,sizeY,sliceZ,angle,fileName,probDiameterSize=83):
    volumeSizeZ=(sizeY+probDiameterSize)*2+1
    if angle ==360:
        volumeSizeY= (sizeY+probDiameterSize)*2+1
    elif angle == 180:
        volumeSizeY= (sizeY+probDiameterSize)+1
    
    mhd_HeaderFileWriter(probAxissizeX,volumeSizeY,volumeSizeZ,fileName)
    volume3d=np.zeros((volumeSizeZ,volumeSizeY,probAxissizeX),dtype=np.uint8)
    stepAngle=(angle/float(sliceZ))
    for indxZ in range(0,volumeSizeZ-1):
        for indxY in range(0,volumeSizeY-1):
            if angle==360:
                cartesianY = indxY-(sizeY+probDiameterSize+1)
            elif angle==180:
                cartesianY = indxY 
            cartesianZ = indxZ -(sizeY+probDiameterSize)
            ## find angle of image on between image slice
            anglePoint = (((atan2(cartesianY,cartesianZ))*180.0/pi)-0.0001+360)%angle
            image1numberZ = int(ceil(anglePoint/ stepAngle))
            image2numberZ = int(floor(anglePoint/ stepAngle))
            image2powerZ =  (stepAngle -(anglePoint % stepAngle+0.001))/stepAngle
            image1powerZ =  1-image2powerZ 
            
            ## find bilateral filter of  piksel  on between two piksel
            pikselDiameterValueOnVolume = hypot(cartesianY,cartesianZ)
            pikselDiameterValueOnImageSlice = sizeY-(pikselDiameterValueOnVolume - probDiameterSize-1)
            upperindexNumberY=int(floor(pikselDiameterValueOnImageSlice))
            downerindexNumberY=int(ceil(pikselDiameterValueOnImageSlice))
            upperindexPowerY= downerindexNumberY-pikselDiameterValueOnImageSlice
            downerindexPowerY = 1-upperindexPowerY
            if image1numberZ == 600:
                image1numberZ =0
                image2numberZ = 599
            if image1numberZ == 0:
                image1numberZ =0
                image2numberZ = 599
            if image1numberZ == image2numberZ:
                image2numberZ=0
            if upperindexNumberY>0 and downerindexNumberY<sizeY:
                #print(upperindexPowerY,upperindexNumberY,downerindexPowerY,downerindexNumberY," ",image1numberZ,image2numberZ)
                N1p1=raw[image1numberZ*probAxissizeX*(sizeY)+upperindexNumberY*probAxissizeX:image1numberZ*probAxissizeX*(sizeY)+upperindexNumberY*probAxissizeX+probAxissizeX]
                N1p2=raw[image1numberZ*probAxissizeX*(sizeY)+downerindexNumberY*probAxissizeX:image1numberZ*probAxissizeX*(sizeY)+downerindexNumberY*probAxissizeX+probAxissizeX]
                N2p1=raw[image2numberZ*probAxissizeX*(sizeY)+upperindexNumberY*probAxissizeX:image2numberZ*probAxissizeX*(sizeY)+upperindexNumberY*probAxissizeX+probAxissizeX]
                N2p2=raw[image2numberZ*probAxissizeX*(sizeY)+downerindexNumberY*probAxissizeX:image2numberZ*probAxissizeX*(sizeY)+downerindexNumberY*probAxissizeX+probAxissizeX]

                total=image1powerZ*(N1p1*upperindexPowerY+N1p2*downerindexPowerY) + image2powerZ*(N2p1*upperindexPowerY+N2p2*downerindexPowerY)
                #print(N1p1.shape,N2p1.shape,N1p2.shape,N2p2.shape)
                #print(image1numberZ,image2numberZ)
                volume3d[indxZ][indxY][:]=total
            else:
                volume3d[indxZ][indxY][:] =  0
    fileData =open("mhd/"+fileName+".raw",'wb')
    fileData.write(volume3d.tostring())
    fileData.close()
    
def mhd_HeaderFileWriter(sizeX,volumeSizeY,volumeSizeZ,nameFile):
    mhdHeadStr ="ObjectType = Image\nNDims = 3\nBinaryData = True\nBinaryDataByteOrderMSB = False\nCompressedData = False\n"
    mhdHeadStr =mhdHeadStr + "ElementType = MET_UCHAR\nAnatomicalOrientation = LPI\nTransformMatrix = -1 0 0 0 -1 0 0 0 1\n"
    mhdHeadStr =mhdHeadStr +"CenterOfRotation = 0 0 0\nElementSpacing = 0.095 0.095 0.095\nDimSize = "
    t = open("mhd/"+str(nameFile)+".mhd", 'wb')
    t.write(mhdHeadStr)
    t.write(str(sizeX)+" "+str(volumeSizeY)+" "+str(volumeSizeZ))
    t.write("\nElementDataFile = ")
    t.write(nameFile+".raw")
    t.close()


