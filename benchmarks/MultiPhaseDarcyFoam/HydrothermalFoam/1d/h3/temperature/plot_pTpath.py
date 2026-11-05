#!/Users/zguo/.pyenv/shims/python
# -*-coding:utf-8-*-
# Plot p-T path of 1D results
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 'Zhikui Guo, 2020/06/03, GEOMAR
# ===============================================================
import os
import sys
from colored import fg, bg, attr
C_GREEN = fg('green')
C_RED = fg('red')
C_BLUE = fg('blue')
C_DEFAULT = attr('reset')
#===============================================================
from matplotlib.animation import FuncAnimation
import matplotlib.animation as animation
import linecache
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['font.family'] = 'Arial'  #default font family
mpl.rcParams['mathtext.fontset'] = 'cm' #font for math
from iapws import IAPWS97
import iapws

# =====================
def getTimes(dirCase):
    datapath=dirCase+'/postProcessing/linesample/'
    datafiles=os.listdir(datapath)
    times=np.array(datafiles,dtype=int)
    times=np.sort(times)
    return times, datapath
dirCase='./'
times,datapath=getTimes(dirCase)
fmt_movie='mp4'
# ====================
def getBollingCurve_water():
    p=np.linspace(0.001, 22, 200)
    T=np.zeros_like(p)
    for i in range(0,len(p)):
        T[i]=iapws.iapws97._TSat_P(p[i])
    return p,T
p_c, T_c=getBollingCurve_water()  # p_c: [MPa]
T_c = T_c - 273.15  # K->C
fig=plt.figure(figsize=(6,3))
ax=plt.gca()
ln,=ax.plot(T_c, p_c)
ax.text(T_c[50]-5, p_c[50],'Boiling curve',ha='right',va='center',color=ln.get_color())
ax.set_xlabel('Temperature ($^{\circ}$C)')
ax.set_ylabel('Pressure (MPa)')
ax.set_xlim(0,550)
ax.set_ylim(0,23)
plt.tight_layout()
# get filename from caseDir

datafile=datapath+str('%.0f'% times[0])+'/data_T_p.xy'
data=np.loadtxt(datafile)
p=data[:,2]/1e6
T=data[:,1]-273.15
xdata, ydata = [], []
ln, = ax.plot([], [], 'r')
time_str=[]
text=ax.text(0.05,0.99,time_str,va='top',ha='left',color=ln.get_color(), fontweight='bold',transform=ax.transAxes)

def update(i):
    print(times[i])
    datafile=datapath+str('%.0f'% times[i])+'/data_T_p.xy'
    data=np.loadtxt(datafile)
    p=data[:,2]/1e6
    T=data[:,1]-273.15
    ln.set_data(T,p)
    text.set_text(str('t = %.1f years'% (times[i]/86400/365)))
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

# 动画参数
interval = 1 #in seconds  
dpi_out=400
issave=True
repeat=False
fmt_movie='mp4'
fname_movie='results_'
writer=animationWriter(fmt_movie)
ani = FuncAnimation(fig, update, len(times),blit=False, interval=interval*1e3,repeat=repeat)

ani.save(fname_movie+'.'+fmt_movie, dpi=dpi_out, writer=writer)