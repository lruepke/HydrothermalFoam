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
levels=60
# data path
model='singlepass_twolimb'
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
triangles,U=pc.Read_VTK_POLYDATA(datapath,'U',name_fmt=name_fmt,coord2km=True,depthPositive=True)
U_norm = np.sqrt(U[:,0]**2 + U[:,1]**2)
# plot
ax_field, ax_cb, CSf, cb,vmin,vmax=pc.plotField(None,triangles, T,figwidth=24)
fig=plt.gcf()
ax_field.xaxis.set_major_locator(MultipleLocator(0.5))
ax_field.xaxis.set_minor_locator(MultipleLocator(0.1))
ax_field.yaxis.set_major_locator(MultipleLocator(0.5))
ax_field.yaxis.set_minor_locator(MultipleLocator(0.1))
ax_field.set_xlabel('x (km)')
ax_field.set_ylabel('Depth (km)')
cb.set_ticks(MultipleLocator(100))
cb.set_label('Temperature ($^{\circ}$C)')
plt.tight_layout(pad=0)
# init plot
for coll in CSf.collections: 
        ax_field.collections.remove(coll) 
datapath=postProcessDataPath+str(times[-1])
filename=datapath+'/'
triangles,T=pc.Read_VTK_POLYDATA(datapath,'T',name_fmt=name_fmt,coord2km=True,depthPositive=True)
# p=[ax_field.tricontourf(triangles,T,levels=levels,cmap=cmap,vmin=vmin,vmax=vmax)]
p=[ax_field.tripcolor(triangles,T,shading='gouraud',cmap=cmap,vmin=vmin,vmax=vmax)]
# quiver=[ax_field.quiver(triangles.x,triangles.y, U[:,0]/U_norm, U[:,1]/U_norm, units='xy', scale=20, headwidth=0.1, headlength=0.1)]
x_text=0.02
y_text=0.98
color_text='w'
if('singlepass' == model):
    x_text=0.45
    color_text='k'
elif('singlepass2' == model):
    x_text=0.25
    color_text='k'
elif('singlepass_twolimb' == model):
    x_text=0.25
    color_text='k'
text=[ax_field.text(x_text,y_text,str('%.1f years' % (times[-1]/86400/365)),color=color_text,fontsize=14,fontweight='bold',ha='left',va='top',transform=ax_field.transAxes)]
# progressbar
pb = ProgressBar(total=len(times),prefix=C_BLUE+'Progress: '+C_DEFAULT, suffix=' Completed'+C_DEFAULT, decimals=3, length=50, fill=C_GREEN+'#', zfill=C_DEFAULT+'-')

def update(i):
    time=times[i]
    p[0].remove()
    text[0].remove()
    datapath=postProcessDataPath+str(time)
    filename=datapath+'/'
    triangles,T=pc.Read_VTK_POLYDATA(datapath,'T',name_fmt=name_fmt,coord2km=True,depthPositive=True)
    # p[0]=ax_field.tricontourf(triangles,T,levels=levels,cmap=cmap,vmin=vmin,vmax=vmax)
    p[0]=ax_field.tripcolor(triangles,T,shading='gouraud',cmap=cmap,vmin=vmin,vmax=vmax)
    text[0]=ax_field.text(x_text,y_text,str('%.1f years' % (time/86400/365)),color=color_text,fontsize=14,fontweight='bold',ha='left',va='top',transform=ax_field.transAxes)
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
    plt.savefig('T_'+model+'.pdf')
    # plt.show()

