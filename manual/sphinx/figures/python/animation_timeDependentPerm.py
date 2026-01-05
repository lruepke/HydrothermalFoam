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
cmap='Spectral_r'
cmap_perm='rainbow'
levels=60
# data path
model='timeDependentPerm'
caseDir='../../../../cookbooks/'+model
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
triangles,perm=pc.Read_VTK_POLYDATA(datapath,'permeability',name_fmt=name_fmt,coord2km=True,depthPositive=True)
# plot
figsize=scifig.figsize_cm(18,x=triangles.x,y=triangles.y,w_offset_cm=2.1)
figsize=(figsize[0],figsize[1]*2)
fig,axs=plt.subplots(2,1,sharex=True,sharey=False,gridspec_kw={"width_ratios":[1],"height_ratios":[1,1]},figsize=figsize)
# temperature
ax_field=axs[0]
ax_field, ax_cb, CSf, cb,vmin,vmax=pc.plotField(ax_field,triangles, T)
ax_field.xaxis.set_major_locator(MultipleLocator(0.5))
ax_field.xaxis.set_minor_locator(MultipleLocator(0.1))
ax_field.yaxis.set_major_locator(MultipleLocator(0.5))
ax_field.yaxis.set_minor_locator(MultipleLocator(0.1))
# ax_field.set_xlabel('x (km)')
ax_field.set_ylabel('Depth (km)')
cb.set_ticks(MultipleLocator(100))
cb.set_label('Temperature ($^{\circ}$C)')

# permeability
ax_perm=axs[1]
ax_perm, ax_cb_perm, CSf_perm, cb_perm,vmin_perm,vmax_perm=pc.plotField(ax_perm,triangles, perm/np.min(perm), cmap=cmap_perm)
ax_perm.xaxis.set_major_locator(MultipleLocator(0.5))
ax_perm.xaxis.set_minor_locator(MultipleLocator(0.1))
ax_perm.yaxis.set_major_locator(MultipleLocator(0.5))
ax_perm.yaxis.set_minor_locator(MultipleLocator(0.1))
ax_perm.set_xlabel('x (km)')
ax_perm.set_ylabel('Depth (km)')
cb_perm.set_ticks(MultipleLocator(1))
cb_perm.set_label('Permeability ($\\times \mathregular{10} ^{\mathregular{-14}}\ \mathregular{m}^{\mathregular{2}}$)')

plt.tight_layout(pad=0)
# init plot
for coll in CSf.collections: 
        ax_field.collections.remove(coll) 
datapath=postProcessDataPath+str(times[-1])
filename=datapath+'/'
# temperature
triangles,T=pc.Read_VTK_POLYDATA(datapath,'T',name_fmt=name_fmt,coord2km=True,depthPositive=True)
pcolor_T=[ax_field.tripcolor(triangles,T,shading='gouraud',cmap=cmap,vmin=vmin,vmax=vmax)]
text=[ax_field.text(0.02,0.98,str('%.1f years' % (times[-1]/86400/365)),color='w',fontsize=14,fontweight='bold',ha='left',va='top',transform=ax_field.transAxes)]
# permbility
triangles,perm=pc.Read_VTK_POLYDATA(datapath,'permeability',name_fmt=name_fmt,coord2km=True,depthPositive=True)
pcolor_perm=[ax_perm.tripcolor(triangles,perm/np.min(perm),shading='gouraud',cmap='rainbow',vmin=vmin_perm,vmax=vmax_perm)]
text_perm=[ax_perm.text(0.02,0.98,str('%.1f years' % (times[-1]/86400/365)),color='w',fontsize=14,fontweight='bold',ha='left',va='top',transform=ax_perm.transAxes)]
# progressbar
pb = ProgressBar(total=len(times),prefix=C_BLUE+'Progress: '+C_DEFAULT, suffix=' Completed'+C_DEFAULT, decimals=3, length=50, fill=C_GREEN+'#', zfill=C_DEFAULT+'-')

def update(i):
    time=times[i]
    datapath=postProcessDataPath+str(time)
    filename=datapath+'/'

    # temperature
    pcolor_T[0].remove()
    text[0].remove()
    triangles,T=pc.Read_VTK_POLYDATA(datapath,'T',name_fmt=name_fmt,coord2km=True,depthPositive=True)
    # p[0]=ax_field.tricontourf(triangles,T,levels=levels,cmap=cmap,vmin=vmin,vmax=vmax)
    pcolor_T[0]=ax_field.tripcolor(triangles,T,shading='gouraud',cmap=cmap,vmin=vmin,vmax=vmax)
    text[0]=ax_field.text(0.02,0.98,str('%.1f years' % (time/86400/365)),color='w',fontsize=14,fontweight='bold',ha='left',va='top',transform=ax_field.transAxes)
    
    # permeability
    pcolor_perm[0].remove()
    text_perm[0].remove()
    triangles,perm=pc.Read_VTK_POLYDATA(datapath,'permeability',name_fmt=name_fmt,coord2km=True,depthPositive=True)
    pcolor_perm[0]=ax_perm.tripcolor(triangles,perm/np.min(perm),shading='gouraud',cmap=cmap_perm,vmin=vmin_perm,vmax=vmax_perm)
    text_perm[0]=ax_perm.text(0.02,0.98,str('%.1f years\n%.2f $\\times $10$^{\mathregular{-14}}$ m$^{\mathregular{2}}$' % (time/86400/365, np.max(perm/np.min(perm)))),color='w',fontsize=14,fontweight='bold',ha='left',va='top',transform=ax_perm.transAxes)
    
    if(time==times[-1]):
        plt.savefig('T_'+model+'.pdf')
    pb.print_progress_bar(i+1)

# 根据不同的movie格式设置相应的writter
def animationWriter(fmt='mp4'):
    if(fmt_movie=='mp4'):
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=15, metadata=dict(artist='Zhikui Guo, et al., 2020, GMD',title='Cookbook of HydrothermalFoam tools',copyright='Zhikui Guo, 2018',comment='HydrothermalFoam open source tools for hydrothermal modeling'), bitrate=1800)
    elif(fmt_movie=='avi'):
        Writer = animation.writers['avconv']
        writer = Writer(fps=15, metadata=dict(artist='Zhikui Guo, et al., 2020, GMD',title='Cookbook of HydrothermalFoam tools',copyright='Zhikui Guo, 2018',comment='HydrothermalFoam open source tools for hydrothermal modeling'), bitrate=1800)
    elif(fmt_movie=='gif'):
        writer='imagemagick'
    else:
        print('暂不支持此movie格式(mp4,gif): ',fmt_movie)
        exit(0)
    return writer
# animation
# 动画参数
interval = 1 #in seconds  
dpi_out=400
issave=True
repeat=False
fmt_movie='mp4'
fname_movie='results_'+model
writer=animationWriter(fmt_movie)
ani = FuncAnimation(fig, update, len(times),blit=False, interval=interval*1e3,repeat=repeat)

# 保存为gif或者显示
if(issave==True):
    ani.save(fname_movie+'.'+fmt_movie, dpi=dpi_out, writer=writer)
else:
    # plt.savefig('result.pdf')
    plt.show()

