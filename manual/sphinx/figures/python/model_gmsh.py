from matplotlib.animation import FuncAnimation
import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import os
from console_progressbar import ProgressBar
from colored import fg, bg, attr
C_GREEN=fg('green')
C_RED=fg('red')
C_BLUE=fg('blue')
C_DEFAULT=attr('reset')


import sciPyFoam.postProcessing.cuttingPlane as pc
import sciPyFoam.figure as scifig

# config font
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['mathtext.fontset'] = 'cm'
scifig.usePaperStyle(mpl,fontsize=12)

# data path
caseDir='../../../../cookbooks/gmsh'
postProcessDataPath=caseDir+'/postProcessing/surfaces/'

times=os.listdir(postProcessDataPath)
timeDirs=[]
for t in times:
    if(os.path.isdir(postProcessDataPath+t)):
        timeDirs.append(t)
    else:
        print(t,'is not a directory')
times=np.array(timeDirs,dtype=int)
times=np.sort(times)

datapath=postProcessDataPath+str(times[-1])
filename=datapath+'/'
name_fmt=lambda  name : name + '_zNormal.vtk'
# read data
triangles,T=pc.Read_VTK_POLYDATA(datapath,'T',name_fmt=name_fmt,coord2km=True,depthPositive=True)

# plot model geometry and boundary conditions

fig=plt.figure(figsize=scifig.figsize_cm(24,x=triangles.x,y=triangles.y))
ax=plt.gca()
plt.axis('scaled')
# ax.triplot(triangles,lw=0.2,color='k')
ax.set_xlim(np.min(triangles.x),np.max(triangles.x))
ax.set_ylim(np.max(triangles.y),np.min(triangles.y))
ax.set_xlabel('x (km)')
ax.set_ylabel('Depth (km)')

# boundary conditions
wspan=0.02
ax.axhspan(ymin=3-wspan,ymax=3,color='r',label='Bottom (heat source)\nT: $fixedValue$ (600$^{\circ}$C)\np: $noFlux$',zorder=4)
ax.axhspan(ymin=2+wspan,ymax=2,color='blue',label='Top (seafloor)\nT: $inletOutlet$ (Inflow T=5$^{\circ}$C, outflow $\\nabla T$ =0)\n p: $fixedValue$ (300 bar)',zorder=4)
ax.axvspan(xmin=0,xmax=wspan,color='gray',label='Sides (insulate impermeable)\nT: $zeroGradient$\np: $noFlux$',zorder=3)
ax.axvspan(xmin=2-wspan,xmax=2,color='gray',zorder=3)
ax.text(0.5,0.5,'Uniform permeability\n$k\ =\ \mathregular{10}^{\mathregular{-14}}\ \mathregular{m}^{\mathregular{2}}$ ',va='center',ha='center',color='purple', fontsize=14,fontweight='bold',transform=ax.transAxes, bbox=dict(boxstyle='round',facecolor='white',alpha=0.8, edgecolor='w'))
ax.legend(loc='upper left', bbox_to_anchor=(0.02,-0.02,1,1),ncol=2)
plt.tight_layout(pad=0)
plt.savefig('model_gmsh.pdf')
plt.savefig('model_gmsh.svg')
# plt.show()