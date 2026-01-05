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
model='singlepass'
caseDir='../../../../cookbooks/'+model
time='0'
patchname='frontAndBack'
# patchname='bottom'
fieldName='T'

# read mesh data
x,y,z, edges=foamToVTK.readPatchMesh(caseDir,patchname,time,coord2km=False,depthPositive=True,eval_patchIndex='((z==np.max(z)) & (x<=300) & (y>=-3925))')

# figure
fig=plt.figure(figsize=scifig.figsize_cm(24,x=x,y=y))
ax=plt.gca()
plt.axis('scaled')
# plot mesh
scifig.polyplot(ax,x,y,edges,linewidth=0.1, color='c')
x2,y2,z2, edges2=foamToVTK.readPatchMesh(caseDir,patchname,time,coord2km=False,depthPositive=True,eval_patchIndex='((z==np.max(z)) & ((x>1000) | (y<=-3925)))')
scifig.polyplot(ax,x2,y2,edges2,linewidth=0.1, color='g')
# plot left boundary
lw_boundary=2
colors_boundary=['m','b','r']
xb,yb,zb,edges2=foamToVTK.readPatchMesh(caseDir,'wall',time,coord2km=False,depthPositive=True)
scifig.polyplot(ax,xb,yb,edges2,linewidth=lw_boundary, color=colors_boundary[0],label='Side walls\np: noFlux\nT: zeroGradient', clip_on=False)
xb,yb,zb,edges2=foamToVTK.readPatchMesh(caseDir,'top',time,coord2km=False,depthPositive=True)
scifig.polyplot(ax,xb,yb,edges2,linewidth=lw_boundary, color=colors_boundary[1],label='Top, p=300 bar\nT: inletOutlet', clip_on=False)
xb,yb,zb,edges2=foamToVTK.readPatchMesh(caseDir,'bottom',time,coord2km=False,depthPositive=True)
scifig.polyplot(ax,xb,yb,edges2,linewidth=0, color=colors_boundary[2],label='Bottom, p: noFlux\nT: codedFixedValue')
ax.legend(ncol=1,labelspacing=1,loc='upper left', bbox_to_anchor=(0.15,0,1,1))
# read bottom T
triangles,T=foamToVTK.readPatch(caseDir,'bottom','160','T',coord2km=False,depthPositive=True)
triangles.y=-triangles.y*10+4000
CS=ax.tripcolor(triangles,T,cmap='rainbow')
# plot colorful legend
ax_cs_legend=ax.inset_axes([0.165,0.62,0.05,0.02], transform=ax.transAxes,zorder=1)
cb2=plt.colorbar(CS, cax=ax_cs_legend, orientation='horizontal')
cb2.outline.set_visible(False)
cb2.solids.set_edgecolor(None)
ax_cs_legend.zorder=10
ax_cs_legend.axis('off')
# color bar
CS2=ax.tripcolor(triangles,T,cmap='rainbow')
ax_cb=ax.inset_axes([0.5,0.2,0.43,0.02], transform=ax.transAxes,zorder=1)
cb=plt.colorbar(CS2, cax=ax_cb, orientation='horizontal')
ax_cb.xaxis.set_ticks_position('top')
ax_cb.xaxis.set_label_position('top')
cb.set_label('Temperature($^{\circ}$C)')
cb.set_ticks(range(0, 400, 25))


# text
bbox=dict(boxstyle='round',facecolor='white',alpha=0.8, edgecolor='w')
txt='Recharge zone\n$k=\mathregular{10}^{\mathregular{-14}}}$ m$^{\mathregular{2}}$'
ax.text(150,3400,txt, ha='center',va='center',bbox=bbox)
txt='Discharge zone\n$k=\mathregular{10}^{\mathregular{-13}}}$ m$^{\mathregular{2}}$'
ax.annotate(txt, xy=(1990,3400), xytext=(1800,3400),color='g',ha='right',va='center', arrowprops=dict(facecolor='black',arrowstyle='->'))

# set axis
ax.set_xlim(np.min(x),np.max(x))
ax.set_ylim(np.max(y)+20,np.min(y))
ax.set_xlabel('x (m)')
ax.set_ylabel('Depth (m)')
# ax.grid(axis='both',which='both',linewidth=0.1,color='k')
ax.xaxis.set_major_locator(MultipleLocator(200))
ax.yaxis.set_major_locator(MultipleLocator(200))
ax.xaxis.set_minor_locator(MultipleLocator(40))
ax.yaxis.set_minor_locator(MultipleLocator(40))
# ax.axis('off')
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)

plt.tight_layout(pad=0.5)
plt.savefig('model_'+model+'.pdf')
# plt.savefig('model_'+model+'.svg')
plt.savefig('model_'+model+'.jpg',dpi=400)
# plt.show()