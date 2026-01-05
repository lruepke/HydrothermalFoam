#!/Users/zguo/.pyenv/shims/python
# -*-coding:utf-8-*-
# Extract valid region from pore network and save to stl
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 'Zhikui Guo, 2020/09/25, GEOMAR
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
import meshio
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import stl

def usage(argv):
    basename = argv[0].split('/')
    basename = basename[len(basename)-1]
    description='Extract valid region from pore network and save to stl'
    num_symbol=int((len(description)+20 - len(basename))/2)
    head='='*num_symbol+basename+'='*num_symbol
    print(head)
    print(description)
    print('Zhikui Guo, 2020/09/25, GEOMAR')
    print('[Example]: '+C_RED + basename+C_BLUE + ' vti/cube.vtu'+C_DEFAULT)
    print('='*len(head))


def blockMeshDict_template():
    blockmeshDict_template="""
    /*--------------------------------*- C++ -*-----------------------------------|
    | =========                 |                                                 |
    | \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
    |  \\    /   O peration     | Version:  5.x                                   |
    |   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
    |    \\/     M anipulation  |                                                 |
    -----------------------------------------------------------------------------*/
    FoamFile
    {
        version     2.0;
        format      ascii;
        class       dictionary;
        object      blockMeshDict;
    }
    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

    convertToMeters 1;

    xmin xmin;
    xmax xmax;
    ymin ymin;
    ymax ymax;
    zmin zmin;
    zmax zmax;

    xcells 100;
    ycells 20;
    zcells 20;

    dx 5;
    dy 5;
    dz 5;

    lx #calc "$xmax - $xmin";
    ly #calc "$ymax - $ymin";
    lz #calc "$zmax - $zmin";

    xcells #calc "floor($lx/$dx)";
    ycells #calc "floor($ly/$dy)";
    zcells #calc "floor($lz/$dz)";

    vertices        
    (
        ($xmin  $ymin  $zmin)
        ($xmax  $ymin  $zmin)
        ($xmax  $ymax  $zmin)
        ($xmin  $ymax  $zmin)
        ($xmin  $ymin  $zmax)
        ($xmax  $ymin  $zmax)
        ($xmax  $ymax  $zmax)
        ($xmin  $ymax  $zmax)
    );

    blocks          
    (
        hex (0 1 2 3 4 5 6 7) ($xcells $ycells $zcells) simpleGrading (1 1 1)
    );

    edges           
    (
    );

    patches         
    (
        patch inlet
        (
            (0 4 7 3)
        )
        patch outlet
        (
            (2 6 5 1)
        )
        patch top
        (
            (1 5 4 0)
        )
        patch bottom 
        (
            (3 7 6 2)
        )
        patch front
        (
            (0 3 2 1)
        )
        patch back
        (
            (4 5 6 7)
        )
    );

    mergePatchPairs 
    (
    );

    // ************************************************************************* //

        """
    return blockmeshDict_template

def scatters2vtu(x,y,z,vtufile):
    npoints,nCells=len(x),len(y)
    fpout=open(vtufile,'w')
    # write vtu
    fpout=open(vtufile,'w')
    fpout.write('<VTKFile type="UnstructuredGrid" version="1.0" byte_order="LittleEndian" header_type="UInt64">\n')
    fpout.write('  <UnstructuredGrid>\n')
    fpout.write('    <Piece NumberOfPoints="%.0f" NumberOfCells="%.0f">\n'%(npoints,nCells))
    fpout.write('      <PointData Scalars="DEM">\n')
    fpout.write('        <DataArray type="Float64" Name="RegionId" format="ascii">\n')
    fpout.write('          ')
    for i in range(0,len(x)):
        fpout.write('%f '%(i))
    fpout.write('\n        </DataArray>\n')
    fpout.write('      </PointData>\n')
    fpout.write('      <CellData>\n')
    fpout.write('      </CellData>\n')
    fpout.write('      <Points>\n')
    fpout.write('        <DataArray type="Float32" Name="Points" NumberOfComponents="3" format="ascii">\n')
    for i in range(0,len(x)):
        fpout.write('          %f %f %f\n'% (x[i],y[i],z[i]))
    fpout.write('        </DataArray>\n')
    fpout.write('      </Points>\n')
    fpout.write('      <Cells>\n')
    fpout.write('        <DataArray type="Int64" Name="connectivity" format="ascii">\n')
    fpout.write('          ')
    for i in range(0,len(x)):
        fpout.write('%.0f '% (i))
    fpout.write('\n        </DataArray>\n')
    fpout.write('        <DataArray type="Int64" Name="offsets" format="ascii">\n')
    fpout.write('          ')
    for i in range(0,nCells):
        fpout.write('1 ')
    fpout.write('\n        </DataArray>\n')
    fpout.write('        <DataArray type="UInt8" Name="types" format="ascii">\n')
    fpout.write('          ')
    VTK_CELLTYPE=1
    for i in range(0,nCells):
        fpout.write('%.0f '%(VTK_CELLTYPE))
    fpout.write('\n        </DataArray>\n')
    fpout.write('      </Cells>\n')
    fpout.write('    </Piece>\n')
    fpout.write('  </UnstructuredGrid>\n')
    fpout.write('</VTKFile>\n')
    
    fpout.close()
def getpatches(x_y_z, value,triangles):
    ind_triangles_patch=(x_y_z[triangles[:,0]]==value)
    ind_triangles_patch=(ind_triangles_patch & (x_y_z[triangles[:,1]]==value))
    ind_triangles_patch=(ind_triangles_patch & (x_y_z[triangles[:,2]]==value))
    return ind_triangles_patch
def construct_stl_mesh(points,triangles_region):
    region = stl.mesh.Mesh(np.zeros(triangles_region.shape[0], dtype=stl.mesh.Mesh.dtype))
    for ii, f in enumerate(triangles_region):
        for jj in range(3):
            region.vectors[ii][jj] = points[f[jj],:]
    return region
def writeBlockMeshDict(bounding,outputfile):
    blockMeshDict=blockMeshDict_template().split('\n')
    fpout=open(outputfile,'w')
    for line in blockMeshDict:
        firstword=line.split(' ')[0]
        if('xmin xmin;' in line):
            fpout.write('\txmin %f;\n'%(bounding[0]))
        elif('xmax xmax;' in line):
            fpout.write('\txmax %f;\n'%(bounding[1]))
        elif('ymin ymin;' in line):
            fpout.write('\tymin %f;\n'%(bounding[2]))
        elif('ymax ymax;' in line):
            fpout.write('\tymax %f;\n'%(bounding[3]))
        elif('zmin zmin;' in line):
            fpout.write('\tzmin %f;\n'%(bounding[4]))
        elif('zmax zmax;' in line):
            fpout.write('\tzmax %f;\n'%(bounding[5]))
        else:
            fpout.write('%s\n'%(line))
    fpout.close()
def process(vtuFile,stlpath):
    porousName=vtuFile.split('/')[-1].split('.')[0]
    stl_regions_path=str('%s/%s'%(stlpath,porousName))
    if(not os.path.exists(stlpath)):
        os.system('mkdir '+stlpath)
        print('  - Creating stl path:',stlpath)
    if(not os.path.exists(stl_regions_path)):
        os.system('mkdir '+stl_regions_path)
        print('  - Creating stl path:',stl_regions_path)
    # 2.1 read vtu 
    print('Reading file')
    print('  - Reading vtu file:',vtuFile)
    mesh = meshio.read(vtuFile)
    # print(mesh)
    # 2.2 get celldata and triangles
    triangles=mesh.cells[0].data
    celldata=mesh.cell_data
    pointdata=mesh.point_data
    xyz=mesh.points
    x,y,z=xyz[:,0],xyz[:,1],xyz[:,2]
    RegionId=pointdata['RegionId']# [0]
    RegionId_unique=np.unique(RegionId)
    num_regions=len(RegionId_unique)
    print('  - All %.0f regions' % (num_regions))
    # print(RegionId.shape,triangles.shape)
    # print('xmin %f;\nxmax %f;\nymin %f;\nymax %f;\nzmin %f;\nzmax %f;'%(np.min(x),np.max(x), np.min(y),np.max(y), np.min(z),np.max(z)))

    print('Extracting regions')
    # 2.4 get inlet, outlet, top, bottom patches: e.g. x of all three vertices of triangle are equal and equal to x_inlet
    print('  - Extracting inlet and outlet patches')
    x_inlet,x_outlet, y_bottom, y_top,z_front,z_back=np.min(x),np.max(x),np.min(y),np.max(y),np.min(z),np.max(z)
    ind_triangles_patches={}
    #     return np.array(triangles_patch)
    ind_triangles_patches['inlet']=getpatches(x,x_inlet,triangles)
    ind_triangles_patches['outlet']=getpatches(x,x_outlet,triangles)
    l_patches=[]
    ind_triangles_allPatches=np.zeros_like(triangles[:,0],dtype=bool)
    ind_triangles_allValidRegions=np.zeros_like(triangles[:,0],dtype=bool)
    ind_triangles_allPatches=(ind_triangles_allPatches|ind_triangles_patches['inlet']|ind_triangles_patches['outlet'])

    # 2.3 get inside point of valid region
    print('  - Extracting valid regions which connect both inlet and outlet patches')
    xyz_pts=[]
    retions_stl=[]
    volume_regions=[]
    l_valid_walls=[]
    for i in range(0,num_regions):
        #print(RegionId_unique[i])
        ind_region_points=(RegionId==RegionId_unique[i])
        #     ind_region=(RegionId==RegionId_unique[i])
        ind_point1_triangles=ind_region_points[triangles[:,0]]
        ind_point2_triangles=ind_region_points[triangles[:,1]]
        ind_point3_triangles=ind_region_points[triangles[:,2]]
        ind_region=((ind_point1_triangles & ind_point2_triangles) & ind_point3_triangles)
        triangles_region=triangles[ind_region]
        #     region_mesh=construct_stl_mesh(mesh.points,triangles_region)
        #     region_mesh.save(str("%s/%.0f.stl"%(stlpath,i)))
        # check valid region: connect both inlet and outlet
        ind_triangles_inlet_valid_region=(ind_region & ind_triangles_patches['inlet'])
        isConnectInlet=(True in ind_triangles_inlet_valid_region)
        isConnectOutlet=(True in (ind_region & ind_triangles_patches['outlet']))
        if(isConnectInlet & isConnectOutlet):
            ind_triangles_allValidRegions=(ind_triangles_allValidRegions|ind_region)
            # get inlet patches of valid region, and then get radom triangle of inlet patch, center of the triangle move, e.g. 0.5, to outlet direction
            triangles_inlet_valid_region=triangles[ind_triangles_inlet_valid_region]
            ind_pt=triangles_inlet_valid_region[int(len(triangles_inlet_valid_region)/2),:]
            x_pt,y_pt,z_pt=np.mean(x[ind_pt])+1,np.mean(y[ind_pt]),np.mean(z[ind_pt])  # ?????
            # plot inside points 
            # ax.plot(x_pt,y_pt,'o',color='k')
            xyz_pts.append(np.array([x_pt,y_pt,z_pt]))
            print('  - Found valid region: index=',i)
    # show fig
    # plt.show()

    # 2.4 write to file
    print('Writing files')
    # 2.4.1 locationInMesh and each region
    print('- Writing locationInMesh')
    fpout=open(str('%s/locationInMesh.txt'%(stl_regions_path)),'w')
    xyz_pts=np.array(xyz_pts,dtype=float)
    for i in range(0,xyz_pts.shape[0]):
        fpout.write('%f\t%f\t%f\n'%(xyz_pts[i,0],xyz_pts[i,1],xyz_pts[i,2]))
    fpout.close()

    # 2.4.3 write the complete STL file and patches
    # complete STL file
    # remove inlet and outlet patches from all valid regions
    print('- Removing inlet and outlet patches from all valid regions')
    for i in range(0,len(ind_triangles_allValidRegions)):
        if(ind_triangles_allPatches[i]):
            ind_triangles_allValidRegions[i]=False
    print('- Constructing STL mesh of all valid regions')
    mesh_walls_noInletOutlet=construct_stl_mesh(mesh.points,triangles[ind_triangles_allValidRegions])
    mesh_walls_noInletOutlet.save(str("%s/%s.stl"%(stlpath,porousName)))
    print('- Writing STL mesh of all valid regions')

    # patches
    print('- Writing STL file of patches')
    for key in ind_triangles_patches.keys():
        print('  - Writing '+key)
        region=construct_stl_mesh(mesh.points,triangles[ind_triangles_patches[key],:])
        region.save(str('%s/%s.stl'%(stl_regions_path,key)))

    # 2.4.4 Write blockMeshDict according to bounding information of the porous geometry
    print('- Writing blockMeshDict')
    writeBlockMeshDict([np.min(x),np.max(x), np.min(y),np.max(y), np.min(z),np.max(z)],str('%s/blockMeshDict'%(stl_regions_path)))


def main(argv):
    argc=len(argv)
    
    if(argc!=2):
        usage(argv)
        exit(0)
    vtufile=argv[1]
    process(vtufile,'stl')

if __name__ == '__main__':
    sys.exit(main(sys.argv))