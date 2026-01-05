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

# ====================
def getBollingCurve_water():
    p=np.linspace(0.001, 22, 200)
    T=np.zeros_like(p)
    for i in range(0,len(p)):
        T[i]=iapws.iapws97._TSat_P(p[i])
    return p,T

# plot p-h space
fig=plt.figure()
ax=plt.gca()
p_sat=np.linspace(0.1, 22.05)
h_sat1=np.zeros_like(p_sat)
h_sat2=np.zeros_like(p_sat)
for i in range(0,len(p_sat)):
    state=IAPWS97(P=p_sat[i], x=0)
    h_sat1[i]=state.h/1000
    state=IAPWS97(P=p_sat[i], x=1)
    h_sat2[i]=state.h/1000
ax.plot(h_sat1, p_sat, color='b')
ax.plot(h_sat2, p_sat, color='b')
ax.set_xlim(0,3)
ax.set_ylim(0,25)
ax.set_xlabel('Specific enthalpy (MJ/kg)')
ax.set_ylabel('Pressure (MPa)')
# calculate state from (p,h)
p=1.49966e+07/1e6
h=1.36506e+06/1E6
# state=IAPWS97(P=p, h=h)
# T=state.T
# print('temperature = ',T)
ax.plot(h,p, marker='.', markerfacecolor='r')
plt.tight_layout()
plt.show()