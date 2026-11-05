import numpy as np 
import matplotlib.pyplot as plt 
import matplotlib as mpl 
from matplotlib.ticker import MultipleLocator
mpl.rcParams['font.family']='Arial'
mpl.rcParams['mathtext.fontset']='cm'

plt.figure(figsize=(5,3))
ax=plt.gca()
x=np.linspace(-3,3,200)
x0=0
qmax=5
qmin=0.5
c=0.5
hf=lambda x: qmin+(qmax-qmin)*np.exp(-((x-x0)**2)/(2*c**2))
y=hf(x)
ax.set_xlim(-3, 3)
ax.set_ylim(0, 5.2)
ax.plot(x,y, color='k')
ax.axvspan(x0-c,x0+c,ymin=0,ymax=hf(c)/(ax.get_ylim()[1] - ax.get_ylim()[0]),facecolor='blue',alpha=0.2)
ax.annotate('',xy=(-c, 2), xycoords='data',xytext=(c, 2), textcoords='data', arrowprops=dict(arrowstyle="<->",color='r'))
ax.text(0, 2, '2c', va='bottom',ha='center')
ax.plot(ax.get_xlim()[0], qmin, marker='o',mfc='r', mec='none', markersize=4, clip_on=False, zorder=4)
ax.text(ax.get_xlim()[0]+0.1, qmin, 'qmin',ha='left', va='bottom',color='r')
ax.hlines(y=qmax,xmin=ax.get_xlim()[0],xmax=0,color='r',ls='dashed')
ax.text(-2, qmax, 'qmax',ha='left', va='top',color='r')
ax.plot(x0, ax.get_ylim()[0], marker='o',mfc='r', mec='none', clip_on=False, markersize=4,zorder=4)
ax.text(x0, ax.get_ylim()[0], 'x0',ha='center', va='bottom',color='r')

ax.set_xlabel('Bottom boundary:x (km)')
ax.set_ylabel('Heat flux (W/m$^{\mathregular{2}}$)')
ax.xaxis.set_major_locator(MultipleLocator(1))
ax.xaxis.set_minor_locator(MultipleLocator(0.2))
ax.yaxis.set_major_locator(MultipleLocator(1))
ax.yaxis.set_minor_locator(MultipleLocator(0.2))

plt.tight_layout()
plt.savefig('Gaussian_hf_2d.pdf')
plt.savefig('Gaussian_hf_2d.svg')

# plt.show()