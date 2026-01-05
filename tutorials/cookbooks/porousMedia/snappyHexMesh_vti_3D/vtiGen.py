#!/Users/zguo/.pyenv/shims/python
# -*-coding:utf-8-*-
# Generate porous meida
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
import porespy as ps
import scipy as sp

def usage(argv):
    basename = argv[0].split('/')
    basename = basename[len(basename)-1]
    description='Generate porous meida'
    num_symbol=int((len(description)+20 - len(basename))/2)
    head='='*num_symbol+basename+'='*num_symbol
    print(head)
    print(description)
    print('Zhikui Guo, 2020/09/27, GEOMAR')
    print('[Example]: '+C_RED + basename+C_BLUE + ' vti/model3D'+C_DEFAULT)
    print('='*len(head))
def porousMediaGeneration(vti_file,x=250,y=250,z=250,por=0.6,blob=3):
    # generate porous network
    im = ps.generators.blobs(shape = [x, y, z], porosity = por, blobiness = blob)
    # Calculate porosity
    porosity = ps.metrics.porosity(im)
    print(porosity)
    # Save to vti
    ps.io.to_vtk(sp.array(im, dtype=int), vti_file) 

def main(argv):
    argc=len(argv)
    if(argc!=2):
        usage(argv)
        exit(0)
    vtifile=argv[1]
    porousMediaGeneration(vtifile)

if __name__ == '__main__':
    sys.exit(main(sys.argv))