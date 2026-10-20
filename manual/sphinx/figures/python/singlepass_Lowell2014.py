
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import sciPyFoam.figure as scifig
# config font
mpl.rcParams['font.family'] = 'Arial'
mpl.rcParams['mathtext.fontset'] = 'cm'
scifig.usePaperStyle(mpl,fontsize=12)


plt.figure(figsize=scifig.figsize_cm(16, 9))
h_l1=0.35
h_l2=1
h_l3=0.2
h_l4=0.3
xkcd=False
if(xkcd):
    plt.xkcd()
x=np.linspace(-np.pi,np.pi,100)
y0=np.sin(x*5)/40
bathy=-0.2+y0
z1=bathy*0.9-h_l1
z2=bathy*0.8-h_l1-h_l2
z3=bathy*0.7-h_l1-h_l2-h_l3
lw=0.5
ymax=0.05
# recharge
x0=-np.pi+0.25
y0=-0.25
c_recharge='k'
plt.annotate("Recharge", xy=(x0, y0), xytext=(x0,0), va="center", ha="center",arrowprops=dict(arrowstyle="->",color=c_recharge))

x0=x0-0.2
plt.annotate("  ", xy=(x0, y0), xytext=(x0,0), va="center", ha="center",arrowprops=dict(arrowstyle="->",color=c_recharge))

x0=x0+0.4
plt.annotate(" ", xy=(x0, y0), xytext=(x0,0), va="center", ha="center",arrowprops=dict(arrowstyle="->",color=c_recharge))

x0=np.pi-0.25
y0=-0.2
plt.annotate("Recharge", xy=(x0, -0.2), xytext=(x0,0.), va="center", ha="center",arrowprops=dict(arrowstyle="->",color=c_recharge))

x0=x0+0.2
plt.annotate(" ", xy=(x0, y0), xytext=(x0,0.), va="center", ha="center",arrowprops=dict(arrowstyle="->",color=c_recharge))

x0=x0-0.4
plt.annotate(" ", xy=(x0, y0), xytext=(x0,0.), va="center", ha="center",arrowprops=dict(arrowstyle="->",color=c_recharge))

# focus flow discharge
y0=-2
plt.annotate(" ", xy=(0, ymax), xytext=(0, -0.3), 
             va="center", ha="center",
                  arrowprops=dict(facecolor='black',shrink=0.03,edgecolor='white',
                                 alpha=1))
plt.text(0,ymax,'Black Smoker\nfield',va='bottom',ha='center',fontweight='bold')

# diffuse flow
x0=-0.5
y0=-0.2
plt.annotate("", xy=(x0, -0.2), xytext=(x0,0), va="center", ha="center",bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="<-",color='gray'))
x0=x0-0.2
plt.annotate("", xy=(x0, -0.2), xytext=(x0,0), va="center", ha="center",bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="<-",color='gray'))
plt.text(x0+0.4,y0+0.2,'',color='gray',ha='right')
x0=0.5
y0=-0.2
plt.annotate("", xy=(x0, -0.2), xytext=(x0,0), va="center", ha="center",bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="<-",color='gray'))
x0=x0+0.2
plt.annotate("", xy=(x0, -0.2), xytext=(x0,0), va="center", ha="center",bbox=dict(boxstyle="round", fc="w"),arrowprops=dict(arrowstyle="<-",color='gray'))
plt.text(x0-0.4,y0+0.15,'Diffuse flow',color='gray',ha='left')

# shallow circulation
x0=-1.0
y0=-0.2
plt.annotate("", xy=(x0, -0.5), xytext=(-0.6,y0),
             arrowprops=dict(arrowstyle = "<-",connectionstyle = "angle3,angleA=90,angleB=0",color='blue'))
x0=-1.5
y0=-0.2
plt.annotate("", xy=(x0, y0), xytext=(-1.0,-0.5),
             arrowprops=dict(arrowstyle = "<-",connectionstyle = "angle3,angleA=180,angleB=90",color='blue'))
x0=-1.5
y0=-0.25
plt.annotate("", xy=(-2.8,-0.6), xytext=(x0, y0),
             arrowprops=dict(arrowstyle = "->",connectionstyle = "angle3,angleA=0,angleB=90",color='blue'))

plt.text(-1.5,-0.2,'Shallow\nCirculation',va='bottom',ha='center')

x0=1.0
y0=-0.2
plt.annotate("", xy=(x0, -0.5), xytext=(0.6,y0),
             arrowprops=dict(arrowstyle = "<-",connectionstyle = "angle3,angleA=90,angleB=0",color='blue'))
x0=1.5
y0=-0.2
plt.annotate("", xy=(x0, y0), xytext=(1.0,-0.5),
             arrowprops=dict(arrowstyle = "<-",connectionstyle = "angle3,angleA=180,angleB=90",color='blue'))
x0=1.6
y0=-0.2
plt.annotate("", xy=(2.8,-0.6), xytext=(x0, y0),
             arrowprops=dict(arrowstyle = "->",connectionstyle = "angle3,angleA=0,angleB=90",color='blue'))

# single pass
# right branch
x0=np.pi-0.25
y0=-0.2-h_l1-h_l2
plt.annotate("", xy=(x0, y0+0.4), xytext=(x0,-0.2-h_l1), va="center", ha="center",
             arrowprops=dict(facecolor='blue',shrink=0.03))
plt.annotate("", xy=(x0-1, y0+0.1), xytext=(x0,y0+0.4),
             arrowprops=dict(shrink=0.03,connectionstyle = "angle3,angleA=90,angleB=0",facecolor='blue'))

plt.annotate("", xy=(0.2,y0+0.4), xytext=(x0-1, y0+0.1),
             arrowprops=dict(shrink=0.03,connectionstyle = "angle3,angleA=180,angleB=90",facecolor='blue'))
plt.annotate("", xy=(0.2,-0.2-h_l1), xytext=(0.2, y0+0.4), va="center", ha="center",
             arrowprops=dict(facecolor='blue',shrink=0.03))
# left branch
x0=-np.pi+0.25
y0=-0.2-h_l1-h_l2
plt.annotate("", xy=(x0, y0+0.4), xytext=(x0,-0.2-h_l1), va="center", ha="center",
             arrowprops=dict(facecolor='blue',shrink=0.03))
plt.annotate("", xy=(x0+1, y0+0.1), xytext=(x0,y0+0.4),
             arrowprops=dict(shrink=0.03,connectionstyle = "angle3,angleA=90,angleB=0",facecolor='blue'))

plt.annotate("", xy=(-0.2,y0+0.4), xytext=(x0+1, y0+0.1),
             arrowprops=dict(shrink=0.03,connectionstyle = "angle3,angleA=180,angleB=90",facecolor='blue'))
plt.annotate("", xy=(-0.2,-0.2-h_l1), xytext=(-0.2, y0+0.4), va="center", ha="center",
             arrowprops=dict(facecolor='blue',shrink=0.03))

plt.annotate("", xy=(0,-0.2-h_l1), xytext=(0, y0+0.4), va="center", ha="center",
             arrowprops=dict(facecolor='red',shrink=0.3,alpha=0.6))
arrow = mpatches.FancyArrowPatch((0, -0.7), (0, -0.2),
                                 mutation_scale=60,facecolor='red',alpha=0.5)
ax=plt.gca()
ax.add_patch(arrow)
# text
plt.text(1.5,-1,'Single Pass',va='center',ha='center',fontweight='bold')
plt.text(-1.5,-1,'Single Pass',va='center',ha='center',fontweight='bold')

# 1. seafloor
plt.plot(x,bathy,color='k',linewidth=lw)
plt.text(np.pi,-0.2,'Seafloor',va='bottom',ha='left',fontweight='bold')
# 2. pillow lavas
plt.plot(x,z1,color='k',linewidth=lw)
plt.fill_between(x,y1=bathy,y2=z1,color=(125/255,205/255,201/255))
plt.text(np.pi,-0.2-h_l1/2,'Pillow\nLavas',va='center',ha='left',fontweight='bold')
plt.text(0,-0.2-h_l1/2,'Focusing',va='center',ha='center',fontweight='bold',fontsize=12)
# 3. sheeted dikes
plt.plot(x,z2,color='k',linewidth=lw)
plt.fill_between(x,y1=z1,y2=z2,color='lightgray')
plt.text(np.pi,-0.2-h_l1-h_l2/2,'Sheeted\ndikes',va='center',ha='left',fontweight='bold')
# 4. liquid magma chamber
plt.plot(x,z3,color='k',linewidth=lw)
plt.fill_between(x,y1=z2,y2=z3,color='red')
plt.text(0,-0.2-h_l1-h_l2-h_l3/2,'Liguid magma chamber',va='bottom',ha='center',fontweight='bold')
# 5. Mushy zone
plt.fill_between(x,y1=z3,y2=-3,color=(146/255,111/255,179/255))
plt.text(0,-0.2-h_l1-h_l2-h_l3-0.05,'Mushy zone',va='top',ha='center',fontweight='bold')
plt.xlim(-np.pi,np.pi)
plt.ylim(-2,0.3)
plt.axis('off')

plt.tight_layout()
# if(xkcd):
#     plt.subplots_adjust(left=0.02,right=0.87,top=1,bottom=0)
#     fig_title='SinglePassModel_xkcd'
# else:
#     plt.subplots_adjust(left=0.02,right=0.9,top=1,bottom=0)
#     fig_title='SinglePassModel'

plt.savefig('singlepass_Lowell2014.pdf')
plt.savefig('singlepass_Lowell2014.jpg',dpi=400)
    
# plt.show()