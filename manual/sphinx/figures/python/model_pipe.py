from matplotlib.animation import FuncAnimation
import matplotlib as mpl
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import os
from console_progressbar import ProgressBar
from colored import fg, bg, attr
C_GREEN=fg('green')
C_RED=fg('red')
C_BLUE=fg('blue')
C_DEFAULT=attr('reset')


import sciPyFoam.postProcessing.foamToVTK as foamToVTK
import sciPyFoam.postProcessing.cuttingPlane as pc
import sciPyFoam.figure as scifig

# config font
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['mathtext.fontset'] = 'cm'
scifig.usePaperStyle(mpl,fontsize=12)

# data path
model='pipe'
caseDir='../../../../cookbooks/'+model
time='0'
patchname='frontAndBack'
# patchname='bottom'
fieldName='T'

# read mesh data
x,y,z, edges=foamToVTK.readPatchMesh(caseDir,patchname,time,coord2km=False,depthPositive=True,eval_patchIndex='((z==np.max(z)) & (y>=-300))')
# figure
fig=plt.figure(figsize=scifig.figsize_cm(24,x=x,y=y))
ax=plt.gca()
plt.axis('scaled')
# plot mesh
scifig.polyplot(ax,x,y,edges,linewidth=0.1, color='c')
x2,y2,z2, edges2=foamToVTK.readPatchMesh(caseDir,patchname,time,coord2km=False,depthPositive=True,eval_patchIndex='((z==np.max(z)) & (y<=-300))')
scifig.polyplot(ax,x2,y2,edges2,linewidth=0.1, color='g')
# plot left boundary
lw_boundary=2
colors_boundary=['m','b','r']
xb,yb,zb,edges2=foamToVTK.readPatchMesh(caseDir,'left',time,coord2km=False,depthPositive=True,eval_patchIndex='x==np.min(x)')
scifig.polyplot(ax,xb,yb,edges2,linewidth=lw_boundary, color=colors_boundary[0],label='Side walls\np: noFlux\nT: zeroGradient', clip_on=False)
xb,yb,zb,edges2=foamToVTK.readPatchMesh(caseDir,'left',time,coord2km=False,depthPositive=True,eval_patchIndex='x!=np.min(x)')
scifig.polyplot(ax,xb,yb,edges2,linewidth=lw_boundary, color=colors_boundary[0])
xb,yb,zb,edges2=foamToVTK.readPatchMesh(caseDir,'wall',time,coord2km=False,depthPositive=True)
scifig.polyplot(ax,xb,yb,edges2,linewidth=lw_boundary, color=colors_boundary[0])
xb,yb,zb,edges2=foamToVTK.readPatchMesh(caseDir,'right',time,coord2km=False,depthPositive=True,eval_patchIndex='x!=np.max(x)')
scifig.polyplot(ax,xb,yb,edges2,linewidth=lw_boundary, color=colors_boundary[0])
xb,yb,zb,edges2=foamToVTK.readPatchMesh(caseDir,'right',time,coord2km=False,depthPositive=True,eval_patchIndex='x==np.max(x)')
scifig.polyplot(ax,xb,yb,edges2,linewidth=lw_boundary, color=colors_boundary[0], clip_on=False)
xb,yb,zb,edges2=foamToVTK.readPatchMesh(caseDir,'top',time,coord2km=False,depthPositive=True)
scifig.polyplot(ax,xb,yb,edges2,linewidth=lw_boundary, color=colors_boundary[1],label='Top, p=300 bar\nT: inletOutlet', clip_on=False)
xb,yb,zb,edges2=foamToVTK.readPatchMesh(caseDir,'bottom',time,coord2km=False,depthPositive=True)
scifig.polyplot(ax,xb,yb,edges2,linewidth=lw_boundary, color=colors_boundary[2],label='Bottom, T=400 $^{\circ}$C\np: flux=1 g/m$^{\mathregular{2}}$/s', clip_on=False)

ax.legend(ncol=2)
bbox=dict(boxstyle='round',facecolor='white',alpha=0.8, edgecolor='w')
txt='Layer 2A, $k=\mathregular{4}\\times\mathregular{10}^{\mathregular{-14}}}$ m$^{\mathregular{2}}$'
ax.text(0,100,txt, ha='center',bbox=bbox)
txt='Layer 2B, $k=\mathregular{10}^{\mathregular{-15}}}$ m$^{\mathregular{2}}$'
ax.annotate(txt, xy=(0,350), xytext=(50,350),ha='left',va='center', arrowprops=dict(facecolor='black',arrowstyle='->'))
# set axis
ax.set_xlim(np.min(x),np.max(x))
ax.set_ylim(np.max(y),np.min(y))
ax.set_xlabel('x (m)')
ax.set_ylabel('Depth (m)')
# ax.grid(axis='both',which='both',linewidth=0.1,color='k')
ax.xaxis.set_major_locator(MultipleLocator(100))
ax.yaxis.set_major_locator(MultipleLocator(100))
ax.xaxis.set_minor_locator(MultipleLocator(20))
ax.yaxis.set_minor_locator(MultipleLocator(20))
ax.axis('off')

plt.tight_layout(pad=0.5)
plt.savefig('model_'+model+'.pdf')
# plt.savefig('model_'+model+'.svg')
plt.savefig('model_'+model+'.jpg',dpi=400)
# plt.show()