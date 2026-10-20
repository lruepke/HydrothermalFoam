#!/Users/zguo/.pyenv/shims/python
# -*-coding:utf-8-*-
# Process vtu data, split boundary patches and porous network walls and save to stl files. Calculate coordinates of point in valid regions.
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 'Zhikui Guo, 2020/09/27, GEOMAR
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
    description='VTU to STL, write blockMeshDict and locationInMesh.txt'
    num_symbol=int((len(description)+20 - len(basename))/2)
    head='='*num_symbol+basename+'='*num_symbol
    print(head)
    print(description)
    print('Zhikui Guo, 2020/09/27, GEOMAR')
    print('[Example]: '+C_RED + basename+C_BLUE + ' vti/model2D.vtu'+C_DEFAULT)
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
    zcells 1;

    dx 2;
    dy 2;
    //dz 5;

    lx #calc "$xmax - $xmin";
    ly #calc "$ymax - $ymin";
    lz #calc "$zmax - $zmin";

    xcells #calc "floor($lx/$dx)";
    ycells #calc "floor($ly/$dy)";
    //zcells #calc "floor($lz/$dz)";

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
def process(vtuFile,stlpath='stl'):
    porousName=vtuFile.split('/')[-1].split('.')[0]
    stl_regions_path=str('%s/%s'%(stlpath,porousName))
    if(not os.path.exists(stlpath)):
        os.system('mkdir '+stlpath)
    if(not os.path.exists(stl_regions_path)):
        os.system('mkdir '+stl_regions_path)
    # 2.1 read vtu 
    mesh = meshio.read(vtuFile)
    mesh.points[:,2]=mesh.points[:,2]*10
    # 2.2 get celldata and triangles
    triangles=mesh.cells[0].data
    celldata=mesh.cell_data
    xyz=mesh.points
    x,y,z=xyz[:,0],xyz[:,1],xyz[:,2]
    RegionId=celldata['RegionId'][0]
    RegionId_unique=np.unique(RegionId)
    num_regions=len(RegionId_unique)
    print('All %.0f regions' % (num_regions))
    # 2.4 get inlet, outlet, top, bottom patches: e.g. x of all three vertices of triangle are equal and equal to x_inlet
    x_inlet,x_outlet, y_bottom, y_top,z_front,z_back=np.min(x),np.max(x),np.min(y),np.max(y),np.min(z),np.max(z)
    ind_triangles_patches={}
    ind_triangles_patches['inlet']=getpatches(x,x_inlet,triangles)
    ind_triangles_patches['outlet']=getpatches(x,x_outlet,triangles)
    ind_triangles_patches['top']=getpatches(y,y_top,triangles)
    ind_triangles_patches['bottom']=getpatches(y,y_bottom,triangles)
    ind_triangles_patches['front']=getpatches(z,z_front,triangles)
    ind_triangles_patches['back']=getpatches(z,z_back,triangles)
    # plot 
    fig=plt.figure(figsize=(12,8))
    ax=plt.gca()
    l_patches=[]
    ind_triangles_allPatches=np.zeros_like(triangles[:,0],dtype=bool)
    for key in ind_triangles_patches.keys():
        if((key=='valid walls')):
            continue
        ind_triangles_allPatches=(ind_triangles_allPatches | ind_triangles_patches[key]) 
        if((key=='front') | (key=='back') | (key=='valid walls')):
            continue
        l=ax.triplot(x,y,triangles[ind_triangles_patches[key],:])
        l_patches.append(l[0])
    # 2.5 remove patches
    ind_triangles_patches['walls']=~ind_triangles_allPatches
    # 2.3 get inside point of each region
    xyz_pts=[]
    retions_stl=[]
    volume_regions=[]
    l_valid_walls=[]
    for i in range(0,num_regions):
        ind_region=(RegionId==RegionId_unique[i])
        triangles_region=triangles[ind_region]
        # get random point inside the region
        ind_pt=triangles_region[int(len(triangles_region)/2),:]
        x_pt,y_pt,z_pt=np.mean(x[ind_pt]),np.mean(y[ind_pt]),np.mean(z)
        # check valid region: connect both inlet and outlet
        isConnectInlet=(True in (ind_region & ind_triangles_patches['inlet']))
        isConnectOutlet=(True in (ind_region & ind_triangles_patches['outlet']))
        if(isConnectInlet & isConnectOutlet):
            wallcolor='red'
            ind_valid_walls=(ind_triangles_patches['walls'] & ind_region)
            l_valid_wall=ax.triplot(x,y,triangles[ind_valid_walls,:])
            l_valid_walls.append(l_valid_wall[0])
            # plot inside points 
            ax.plot(x_pt,y_pt,'o',color='k')
            xyz_pts.append(np.array([x_pt,y_pt,z_pt]))
        else:
            ax.triplot(x,y,triangles[(ind_triangles_patches['walls'] & ind_region),:],color='gray')
    # legends
    leg_patches=plt.legend(handles=l_patches,labels=ind_triangles_patches.keys(),
                        loc='lower right',title='Valid regions',bbox_to_anchor=(0.12,0,1,1))
    ax.add_artist(leg_patches)
    labels_valid_walls=list(np.linspace(1,len(l_valid_walls),len(l_valid_walls),dtype=int))
    leg_walls=plt.legend(handles=l_valid_walls,labels=labels_valid_walls,
                        loc='upper right',title='Valid walls',bbox_to_anchor=(0.12,0,1,1))
    plt.tight_layout()
    # plt.savefig('porous_location_regions.png',dpi=500)
    plt.show()
    # 2.4 write to file
    # 2.4.1 locationInMesh and each region
    xyz_pts=np.array(xyz_pts)
    fpout=open(str('%s/locationInMesh.txt'%(stl_regions_path)),'w')
    for i in range(0,xyz_pts.shape[0]):
        fpout.write('%f\t%f\t%f\n'%(xyz_pts[i,0],xyz_pts[i,1],xyz_pts[i,2]))
    fpout.close()
    # patches
    for key in ind_triangles_patches.keys():
        region=construct_stl_mesh(mesh.points,triangles[ind_triangles_patches[key],:])
        region.save(str('%s/%s.stl'%(stl_regions_path,key)))
    # 2.4.4 Write blockMeshDict according to bounding information of the porous geometry
    writeBlockMeshDict([np.min(x),np.max(x), np.min(y),np.max(y), np.min(z),np.max(z)],str('%s/blockMeshDict'%(stl_regions_path)))



def main(argv):
    argc=len(argv)
    if(argc!=2):
        usage(argv)
        exit(0)
    vtuFile=argv[1]
    process(vtuFile)

if __name__ == '__main__':
    sys.exit(main(sys.argv))