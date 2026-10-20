#!/Users/zguo/.pyenv/shims/python
# -*-coding:utf-8-*-
# Thermal equilibrium curve
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 'Zhikui Guo, 2020/06/04, GEOMAR
# ===============================================================

import sys
from colored import fg, bg, attr
C_GREEN = fg('green')
C_RED = fg('red')
C_BLUE = fg('blue')
C_DEFAULT = attr('reset')
#===============================================================
import linecache
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl
mpl.rcParams['font.family'] = 'Arial'  #default font family
mpl.rcParams['mathtext.fontset'] = 'cm' #font for math
import iapws 
from iapws import IAPWS97

def usage(argv):
    basename = argv[0].split('/')
    basename = basename[len(basename)-1]
    description='Thermal equilibrium curve'
    num_symbol=int((len(description)+20 - len(basename))/2)
    head='='*num_symbol+basename+'='*num_symbol
    print(head)
    print(description)
    print('Zhikui Guo, 2020/06/04, GEOMAR')
    print('[Example]: '+C_RED + basename+C_BLUE + ' '+C_DEFAULT)
    print('='*len(head))
def thermalEqui_T(p,h,mass,T0, rho_r=2700, cp_r=880, poro=0.1):
    H_r = rho_r*cp_r*(1-poro)*T0
    H_f = mass*h*poro
    H_t=H_r + H_f 
    print(H_r, H_f, H_t)
    # 1. TEMPERATURE
    T=np.linspace(5, 700, 800) + 273.15
    H=np.zeros_like(T)
    for i in range(0,len(T)):
        H_r = rho_r*cp_r*(1-poro)*T[i]
        state = IAPWS97(P=p/1e6, T=T[i])
        h_f = state.h*1000
        rho_f = state.rho
        H_f = poro*rho_f*h_f
        H[i]=H_f+H_r -H_t
    # calculate T_c, h_fc
    return T, H
def thermalEqui_h(p,h,mass,T0, rho_r=2700, cp_r=880, poro=0.1):
    H_r = rho_r*cp_r*(1-poro)*T0
    H_f = mass*h*poro
    H_t=H_r + H_f 
    # print(H_r, H_f, H_t)
    # 1. TEMPERATURE
    h_f=np.linspace(0.5, 4, 100) # MJ/kg
    H=np.zeros_like(h_f)
    T=np.zeros_like(h_f)
    for i in range(0,len(h_f)):
        state = IAPWS97(P=p/1e6, h=h_f[i]*1000)
        rho_f = state.rho
        T[i] = state.T
        H_f = poro*rho_f*h_f[i]*1e6
        H_r = rho_r*cp_r*(1-poro)*T[i]
        H[i]=H_f+H_r -H_t
    # calculate T_c, h_fc
    T_c = iapws.iapws97._TSat_P(p/1e6)
    H_rc = rho_r*cp_r*(1-poro)*T_c
    H_fc = H_t - H_rc
    state=IAPWS97(P=p/1e6, T=T_c)
    h_fc = H_fc/(poro*mass)
    print(T_c, h_fc/1000,state.rho)
    return h_f, H, T,T_c, h_fc
def plot_thermalEqui(p,h,mass,T0, rho_r=2700, cp_r=880, poro=0.1):
    h_f, H, T, T_c, h_fc=thermalEqui_h(p,h,mass,T0,rho_r,cp_r,poro)

    fig,axs=plt.subplots(1,2,figsize=(12,4))
    ax=axs[0]

    H=H/1e6
    ln_H=ax.plot(h_f, H, marker='.',markerfacecolor='r',color='b',markersize=1,markeredgecolor='None',linewidth=0.2)
    ax.set_xlim(np.min(h_f),np.max(h_f))
    # ax.set_ylim(np.min(H),np.max(H))
    ax.set_ylim(-200,200)
    ax.hlines(y=0,xmin=ax.get_xlim()[0],xmax=ax.get_xlim()[1], linestyle=':',color=ln_H[0].get_color())
    ax.set_xlabel('Specific enthalpy of fluid (MJ/kg)')
    ax.set_ylabel('$H(h) = H_r + H_f - H_t$ (MJ/kg)',color=ln_H[0].get_color())
    ax.tick_params(axis='y',colors=ln_H[0].get_color())
    ax.vlines(h/1e6,ax.get_ylim()[0],ax.get_ylim()[1],lw=1,color='k',ls='--')
    ax.text(h/1e6+0.05, -150, '$h$',va='center',ha='left')
    ax.vlines(h_fc/1000, ax.get_ylim()[0],ax.get_ylim()[1],lw=1,color='k',ls='--')
    ax2=ax.twinx()
    ln_T=ax2.plot(h_f,T,'g',linewidth=0.2,marker='.',markersize=1,markerfacecolor='r',markeredgecolor='None')
    ax2.set_ylabel('Equilibrium temperature (K)',color=ln_T[0].get_color())
    ax2.tick_params(axis='y',colors=ln_T[0].get_color())
    ax.xaxis.set_major_locator(ticker.MultipleLocator(0.5))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(0.1))
    # ax.grid(axis='both',which='both')
    # text
    ax.text(0.02,0.98,str('$p$ = %.5f MPa\n$h$ = %.5e MJ/kg\n$M_f$ = %.5f $kg/m^3$\n$T_0$ = %.1f K = %.1f $^{\circ}$C\nporosity = %.1f\n$\\rho_r$ = %.0f $kg/m^3$\n$C_{pr}$ = %.0f $J/kg/K$'% (p/1e6,h,mass,T0,T0-273.15,poro,rho_r,cp_r)),va='top',ha='left',transform=ax.transAxes)
    # Tup, Tdown
    ax2.hlines(y=T0, xmin=ax2.get_xlim()[0],xmax=ax2.get_xlim()[1], color=ln_T[0].get_color(),linestyle='--',lw=0.5)
    ax2.text(ax2.get_xlim()[1]-0.2, T0, '$T_0$',ha='right',va='bottom')

    # -----------using T
    # T, H = thermalEqui_T(p,h,mass,T0,rho_r,cp_r,poro)
    ax12=axs[1]
    ln_H=ax12.plot(T,H,linewidth=1,marker='.',markersize=1,mfc='r',mec='None',color='b')
    ax12.set_xlim(np.min(T),np.max(T))
    ax12.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1])
    ax12.hlines(0,ax12.get_xlim()[0],ax12.get_xlim()[1],color=ln_H[0].get_color(),ls='--',lw=0.5)
    ax12.yaxis.set_ticks_position('right')
    ax12.yaxis.set_label_position('right')
    ax12.set_ylabel(ax.get_ylabel(),color=ln_H[0].get_color())
    ax12.tick_params(axis='y',colors=ln_H[0].get_color())
    ax12.set_xlabel(ax2.get_ylabel(), color=ln_T[0].get_color())
    ax12.tick_params(axis='x',colors=ln_T[0].get_color())
    ax12.vlines(T0, ax12.get_ylim()[0],ax12.get_ylim()[1],color='g',ls='--',lw=0.5)
    ax12.text(T0+20, -150, '$T_0$',va='center',ha='left')
    plt.tight_layout()
    # plt.show()
    plt.savefig('thermalEquilibrium_h.pdf')

def main(argv):
    argc=len(argv)
    if(argc!=1):
        usage(argv)
        exit(0)
    # plot_thermalEqui(p=1.49966e+07, h=3.15816e+06, mass=3.53992, T0=623.15)
    plot_thermalEqui(p=1.28918e+07, h=3.15816e+06, mass=3.53992, T0=623.15)

if __name__ == '__main__':
    sys.exit(main(sys.argv))