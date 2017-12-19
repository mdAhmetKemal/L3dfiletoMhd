import numpy as np
import struct
import binascii
import zlib,sys
from  rawDatato3dVolume import *

def fileSpesification_DataFinder(L3DfileName):
    with open(L3DfileName, 'rb') as file:
        file.seek(79)
        temp_Loadedfile = file.read()
        file.close()

    templeTuple = struct.unpack("<bb", str(temp_Loadedfile[0:2]))

    if "(40, 0)" == str(templeTuple):
        ##this find 3d volume data size from file
        binarySizeXYZ = str(temp_Loadedfile[6:10])+\
        str(temp_Loadedfile[18:22])+\
        str(temp_Loadedfile[30:34])
        all_integerSizeX_Y_Z = struct.unpack("<iii ", binarySizeXYZ)
        Slice2dImagesizeX =all_integerSizeX_Y_Z[0]
        Slice2dImagesizeY =all_integerSizeX_Y_Z[1]
        SliceNumberZ =all_integerSizeX_Y_Z[2]
        ##this find patient spesification
        patientProtokol =  str(temp_Loadedfile[42:52])
        patientName =  str(temp_Loadedfile[62:73])

    ##--Find file matematical Spesification from file
    count =0
    triple_xFF =0
    SpesificationArray =np.zeros(200,dtype=np.int)
    while "(0,)" != str(templeTuple)  :
        triple_xFF = int(temp_Loadedfile.find("03ff".decode("hex"),triple_xFF+2))
        templeTuple = struct.unpack("<b", str(temp_Loadedfile[triple_xFF+2:triple_xFF+3]))
        templeTuple2 = struct.unpack("<h", str(temp_Loadedfile[triple_xFF+6:triple_xFF+8]))
        SpesificationArray[count] = templeTuple2[0]
        count = count + 1
        
        templeTuple2 = struct.unpack("<h", str(temp_Loadedfile[triple_xFF+8:triple_xFF+10]))
        SpesificationArray[count] = templeTuple2[0]
        count = count + 1
    triple_xFF=int(temp_Loadedfile.find("03ff".decode("hex"),triple_xFF+3))
    templeTuple2 = struct.unpack("<III", str(temp_Loadedfile[triple_xFF+2:triple_xFF+14]))
    usgAngle =  SpesificationArray[17]
    
    #zlib decompressed image file 
    decompresObject= zlib.decompressobj(zlib.MAX_WBITS|32)
    zippedFilePart = str(temp_Loadedfile[triple_xFF+18:len(temp_Loadedfile)])
    decompanseFile=  decompresObject.decompress(zippedFilePart)
 
    #Control between file length
    if len(decompanseFile)== templeTuple2[2]:
        print  ( "zlib successful")
    else :
        print ( "zlib unsuccessful!!")
        
    #--write file spesification
    if True:
        print("Patient Name: ",patientName,"  ","Patient Protokol: ",patientProtokol)
        print("Volume X size:",Slice2dImagesizeX," ","Volume Y size:",Slice2dImagesizeY," ",\
              "Volume Z size:",SliceNumberZ,"Angle:", usgAngle)
    rawArrayUint8=np.fromstring(decompanseFile,dtype=np.uint8)
    ## --volume Function write same folder  mhd file
    volumeFinder(rawArrayUint8,Slice2dImagesizeX,Slice2dImagesizeY,\
                 SliceNumberZ,usgAngle,L3DfileName,probDiameterSize=83)
