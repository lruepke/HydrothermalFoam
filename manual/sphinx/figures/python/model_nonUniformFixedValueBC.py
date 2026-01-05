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


import sciPyFoam.postProcessing.cuttingPlane as pc
import sciPyFoam.figure as scifig

# config font
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['mathtext.fontset'] = 'cm'
scifig.usePaperStyle(mpl,fontsize=12)

# data path
caseDir='../../../../cookbooks/helloworld'
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
ax.xaxis.set_major_locator(MultipleLocator(0.25))
ax.xaxis.set_minor_locator(MultipleLocator(0.05))
# boundary conditions
wspan=0.02
# 
x=np.linspace(0,2,100)
y=np.linspace(3-wspan,3,2)
X,Y=np.meshgrid(x,y)
wGauss=0.2
x0=1
Tmin=573.15-273.15
Tmax=873.15-273.15
funcT = lambda x : Tmin+(Tmax-Tmin)*np.exp(-(x-x0)**2/(2*wGauss**2))
bc_T=funcT(X)
im = plt.imshow(bc_T, interpolation='bilinear', cmap='Spectral_r', origin='lower', extent=[0, 1, 0,0.03],zorder=4,transform=ax.transAxes)
axin=ax.inset_axes([0, 0, 1,0.03],transform=ax.transAxes,facecolor=None,zorder=3)
axin.xaxis.set_ticks_position('top')
axin.yaxis.set_ticks([])
axin.spines['left'].set_visible(False)
axin.spines['right'].set_visible(False)
axin.spines['bottom'].set_visible(False)
axin.set_xlim(ax.get_xlim())
axin.xaxis.set_major_locator(MultipleLocator(0.25))
axin.xaxis.set_minor_locator(MultipleLocator(0.05))
# change tick labels to temperature
xticklabels=axin.get_xticks().tolist()
for i in range(0,len(xticklabels)):
    if(float(xticklabels[i])<0.25 or float(xticklabels[i])>1.75):
        xticklabels[i]=''
    else:
        xticklabels[i]=str(('%.0f $^{\circ}$C') % funcT(float(xticklabels[i])))
axin.set_xticklabels(xticklabels,fontsize=9)
# 
ax.axhspan(ymin=3-wspan,ymax=3,color='w',label='Bottom (heat source)\nT: $codedFixedValue$ (nonuniform)\np: $noFlux$',alpha=0)
ax.axhspan(ymin=2+wspan,ymax=2,color='blue',label='Top (seafloor)\nT: $inletOutlet$ (Inflow T=5$^{\circ}$C, outflow $\\nabla T$ =0)\n p: $fixedValue$ (300 bar)',zorder=4)
ax.axvspan(xmin=0,xmax=wspan,color='gray',label='Sides (insulate impermeable)\nT: $zeroGradient$\np: $noFlux$',zorder=3)
ax.axvspan(xmin=2-wspan,xmax=2,color='gray',zorder=3)
ax.text(0.5,0.5,'Uniform permeability\n$k\ =\ \mathregular{10}^{\mathregular{-14}}\ \mathregular{m}^{\mathregular{2}}$ ',va='center',ha='center',color='purple', fontsize=14,fontweight='bold',transform=ax.transAxes)
ax.legend(loc='upper left', bbox_to_anchor=(0.02,-0.02,1,1),ncol=2)
im = plt.imshow(bc_T, interpolation='bilinear', cmap='Spectral_r', origin='lower', extent=[0.036,0.08,0.87,0.9],zorder=10,transform=ax.transAxes)

plt.tight_layout(pad=0)
plt.savefig('model_nonUniformFixedValueBC.pdf')
plt.savefig('model_nonUniformFixedValueBC.svg')
# plt.show()