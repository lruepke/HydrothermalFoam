import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib as mpl 
from matplotlib.ticker import MultipleLocator
mpl.rcParams['font.family']='Arial'
mpl.rcParams['mathtext.fontset']='cm'

plt.figure(figsize=(5,3))
ax=plt.gca()
x=np.linspace(0,2,200)
x0=1
qmax=873.15
qmin=573
c=0.2
hf=lambda x: qmin+(qmax-qmin)*np.exp(-((x-x0)**2)/(2*c**2))
y=hf(x)
ax.set_xlim(np.min(x),np.max(x))
ax.set_ylim(np.min(y)-10,np.max(y)+10)
ax.plot(x,y, color='k')
ymax=(hf(x0-c)-ax.get_ylim()[0])/(ax.get_ylim()[1] - ax.get_ylim()[0])
ax.axvspan(x0-c,x0+c,ymin=0,ymax=ymax,facecolor='green',alpha=0.2)
y0=650
ax.annotate('',xy=(x0-c, y0), xycoords='data',xytext=(x0+c, y0), textcoords='data', arrowprops=dict(arrowstyle="<->",color='r'))
ax.text(x0, y0+10, '2 wGauss', va='bottom',ha='center')
ax.plot(ax.get_xlim()[0], qmin, marker='o',mfc='r', mec='none', markersize=4, clip_on=False, zorder=4)
ax.text(ax.get_xlim()[0]+0.1, qmin, 'Tmin',ha='left', va='bottom',color='r')
ax.hlines(y=qmax,xmin=ax.get_xlim()[0],xmax=x0,color='r',ls='dashed')
ax.text(0.3, qmax-5, 'Tmax',ha='left', va='top',color='r')
ax.plot(x0, ax.get_ylim()[0], marker='o',mfc='r', mec='none', clip_on=False, markersize=4,zorder=4)
ax.text(x0, ax.get_ylim()[0], 'x0',ha='center', va='bottom',color='r')

ax.set_xlabel('Bottom boundary:x (km)')
ax.set_ylabel('Temperature (K)')
ax.xaxis.set_major_locator(MultipleLocator(0.2))
ax.xaxis.set_minor_locator(MultipleLocator(0.04))
ax.yaxis.set_major_locator(MultipleLocator(50))
ax.yaxis.set_minor_locator(MultipleLocator(10))

plt.tight_layout()
plt.savefig('Gaussian_T_2d.pdf')
plt.savefig('Gaussian_T_2d.svg')

# plt.show()