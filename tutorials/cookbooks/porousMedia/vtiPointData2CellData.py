#!/Users/zguo/.pyenv/shims/python
# -*-coding:utf-8-*-
# Convert PointData in vti file to CellData
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 'Zhikui Guo, 2020/10/01, GEOMAR
# ===============================================================

import sys
import argparse
import sys
import os
from colored import fg, bg, attr
C_GREEN = fg('green')
C_RED = fg('red')
C_BLUE = fg('blue')
C_DEFAULT = attr('reset')
#===============================================================
import numpy as np
from vtk import vtkXMLImageDataReader 
from vtk.util import numpy_support as VN
import porespy as ps

def usage(argv):
    basename = argv[0].split('/')
    basename = basename[len(basename)-1]
    description='Convert point data in vti file to CellData'
    num_symbol=int((len(description)+20 - len(basename))/2)
    head='='*num_symbol+basename+'='*num_symbol
    print(head)
    print(description)
    print('Zhikui Guo, 2020/10/01, GEOMAR')
    print('[Example]: '+C_RED + basename+C_BLUE + ' vti/xx.vti'+C_DEFAULT)
    print('='*len(head))

def pointData2CellData(filename):
    print('- Reading the vti file:',filename)
    reader = vtkXMLImageDataReader()
    reader.SetFileName(filename)
    reader.Update()
    data = reader.GetOutput()
    dim = data.GetDimensions()
    if(data.GetPointData().GetNumberOfArrays()<1):
        print('There is no point data in ',filename)
        exit(0)
    arrayName=data.GetPointData().GetArrayName(0)
    pointData=data.GetPointData().GetArray(arrayName)
    print('- Getting the point data array:',arrayName)
    pointData = VN.vtk_to_numpy(data.GetPointData().GetArray(arrayName))
    print('- Point data value(unique): ',np.unique(pointData))
    print('- Dimensions: ',dim)
    print('- Constructing cell data')
    cellData=np.zeros(dim)
    if(len(pointData.shape)>1):
        pointData=pointData[:,0]
    pointData=pointData.reshape((dim[2],dim[1],dim[0]))
    for i in range(0,dim[0]):
        for j in range(0,dim[1]):
            for k in range(0,dim[2]):
                cellData[i][j][k]=pointData[k][j][i]
    newVtiFile=filename.split('.')[0]+'_celldata.vti'
    print('- Writing to vti file:',newVtiFile)
    ps.io.to_vtk(cellData, newVtiFile)

def main(argv):
    argc=len(argv)
    if(argc!=2):
        usage(argv)
        exit(0)
    filename=argv[1]
    pointData2CellData(filename)

if __name__ == '__main__':
    sys.exit(main(sys.argv))

    
