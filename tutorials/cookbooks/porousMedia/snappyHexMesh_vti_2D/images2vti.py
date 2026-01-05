#!/Applications/ParaView-5.4.0.app/Contents/bin/pvpython
import sys
import os
from paraview import simple

imageStack = simple.PNGSeriesReader(
    FileNames=[
        '/Users/zguo/Desktop/porous_1.png',
        '/Users/zguo/Desktop/porous_2.png'
    ],
    DataSpacing=[1,1,1])
print(imageStack.CellData.GetFieldData())
print(dir(imageStack.CellData.GetFieldData))
simple.SaveData('test.vti', proxy=imageStack, CompressorType='ZLib')