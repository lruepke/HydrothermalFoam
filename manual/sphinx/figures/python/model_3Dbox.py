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
model='3Dbox'
caseDir='../../../../cookbooks/'+model
time='7'
# patchname='frontAndBack'
patchname='bottom'
fieldName='T'

# read data
triangles,T=foamToVTK.readPatch(caseDir,patchname,time,fieldName,coord2km=True,depthPositive=True)

# plot
ax_field, ax_cb, CSf, cb,vmin,vmax=scifig.tripcolor(None,triangles, T,figwidth=12,w_offset_cm=3)
cb.set_label('Temperature ($^{\circ}$C)')
ax=ax_field
ax.set_xlim(np.min(triangles.x),np.max(triangles.x))
ax.set_ylim(np.max(triangles.y),np.min(triangles.y))
ax.set_xlabel('x (km)')
ax.set_ylabel('z (km)')
# ax.grid(axis='both',which='both',linewidth=0.1,color='k')
ax.xaxis.set_major_locator(MultipleLocator(0.5))
ax.yaxis.set_major_locator(MultipleLocator(0.5))
ax.xaxis.set_minor_locator(MultipleLocator(0.1))
ax.yaxis.set_minor_locator(MultipleLocator(0.1))
ax_cb.yaxis.set_minor_locator(MultipleLocator(10))

plt.tight_layout(pad=0)
plt.savefig('model_'+model+'.pdf')
plt.savefig('model_'+model+'.jpg',dpi=400)
# plt.show()