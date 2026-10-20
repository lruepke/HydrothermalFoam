#!/Applications/ParaView-5.4.0.app/Contents/bin/pvpython
import sys
import os
from paraview import simple

def step_vti2vtu(vtifile,scalar_clip=0.5):
    vtufile=vtifile.split('.')[0]+'.vtu'
    vtufile_solid=vtifile.split('.')[0]+'_solid.vtu'
    # step : vti to vtu with connectivity
    print("==== Step 2: extract porous surface from vti file and calculate connectivity, then save to vtu file")
    print('  - Opening '+vtifile)
    data = simple.OpenDataFile(vtifile)
    print(str('  - Cliping: Scalars = %f'% (scalar_clip)))
    data_clip = simple.Clip(data, ClipType = 'Scalar', Scalars = ['CELLS', 'im'], Value = scalar_clip)
    print('  - Extracting surface ')
    data_extract = simple.ExtractSurface(data_clip)
    print('  - Triangulating surface')
    data_triang = simple.Triangulate(data_extract)
    print('  - Calculating connectivity ')
    connectivity = simple.Connectivity(Input=data_triang)
    print('  - Saving data to '+vtufile)
    simple.SaveData(vtufile, proxy = connectivity,DataMode='Binary')
    # save solid part as vtu 
    solid_clip = simple.Clip(data, ClipType = 'Scalar', Scalars = ['CELLS', 'im'], Value = scalar_clip,InsideOut=1)
    solid_scaled = simple.Transform(solid_clip, Transform = 'Transform')
    solid_scaled.Transform.Scale = [1e-6, 1e-6, 1e-6]
    simple.SaveData(vtufile_solid, proxy = solid_scaled,DataMode='Binary')

def usage(argv):
    basename = argv[0].split('/')
    basename = basename[len(basename)-1]
    description='Extract porous surface from vti file using paraview, and then save as vtu file'
    num_symbol=int((len(description)+20 - len(basename))/2)
    head='='*num_symbol+basename+'='*num_symbol
    print(head)
    print(description)
    print('Zhikui Guo, 2020/09/27, GEOMAR')
    print('[Example]: ' + basename + ' vti/model2D.vti')
    print('='*len(head))

def main(argv):
    argc=len(argv)
    if(argc!=2):
        usage(argv)
        exit(0)
    vtifile=argv[1]
    step_vti2vtu(vtifile)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
