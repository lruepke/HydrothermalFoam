#!/Users/zguo/.pyenv/shims/python
# -*-coding:utf-8-*-
# Plot 1D result of HydrothermalFoam
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# 'Zhikui Guo, 2020/05/22, GEOMAR
# ===============================================================
import os
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
import matplotlib as mpl
mpl.rcParams['font.family'] = 'Arial'  #default font family
mpl.rcParams['mathtext.fontset'] = 'cm' #font for math
from matplotlib.ticker import MultipleLocator

def usage(argv):
    basename = argv[0].split('/')
    basename = basename[len(basename)-1]
    description='Plot 1D result of HydrothermalFoam: 1D benchmark test'
    num_symbol=int((len(description)+20 - len(basename))/2)
    head='='*num_symbol+basename+'='*num_symbol
    print(head)
    print(description)
    print('Zhikui Guo, 2020/05/22, GEOMAR')
    print('[Example]: '+C_RED + basename+C_BLUE + ' time(7884000000)'+C_DEFAULT)
    print('='*len(head))

def plot_1d(time_str):
    label1='enthalpy'
    label2='temperature'
    label3='HYDROTHERMAL'
    filename1=label1+'/postProcessing/linesample/'+time_str+'/data_T_p.xy'
    filename2=label2+'/postProcessing/linesample/'+time_str+'/data_T_p.xy'
    # filename_HT='../../../USGS_HYDROTHERMAL/1d/h1/h1_T_p_250.0.txt'
    data=np.loadtxt(filename1)
    x=data[:,0]/1000 # km
    T=data[:,1]-273.15 # deg. C
    p=data[:,2]/1e6 # MPa
    data2=np.loadtxt(filename2)
    x2=data2[:,0]/1000 # km
    T2=data2[:,1]-273.15 # deg. C
    p2=data2[:,2]/1e6 # MPa
    # data3=np.loadtxt(filename_HT,skiprows=1)
    # x3=data3[:,0]/1000 # km
    # T3=data3[:,1] # deg. C
    # p3=data3[:,2]/1e6 # MPa

    fig=plt.figure(figsize=(5,4))
    ax=plt.gca()
    ln_T,=ax.plot(x,T,color='r',label=label1)
    ln_T2,=ax.plot(x2,T2,color='r',linestyle=':',label=label2)
    # ln_T3,=ax.plot(x3,T3,color='r',linestyle='-.',label=label3)
    leg=ax.legend()
    ax2=plt.twinx()
    ln_p,=ax2.plot(x,p,color='b')
    ln_p2,=ax2.plot(x2,p2,color='b',linestyle=':')
    # ln_p3,=ax2.plot(x3,p3,color='b',linestyle='-.')
    # set axis
    ax.set_xlim(np.min(x),np.max(x))
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.xaxis.set_minor_locator(MultipleLocator(0.2))
    ax.set_ylim(np.min(T),np.max(T))
    ax.yaxis.set_major_locator(MultipleLocator(50))
    ax.yaxis.set_minor_locator(MultipleLocator(10))
    ax2.set_ylim(np.min(p),np.max(p))
    ax2.yaxis.set_major_locator(MultipleLocator(5))
    ax2.yaxis.set_minor_locator(MultipleLocator(1))
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('Temperature ($^{\circ}$C)')
    ax2.set_ylabel('Pressure (MPa)')
    ax.yaxis.label.set_color(ln_T.get_color())
    ax.tick_params(axis='y', which='both',colors=ln_T.get_color())
    ax2.yaxis.label.set_color(ln_p.get_color())
    ax2.tick_params(axis='y', which='both',colors=ln_p.get_color())
    plt.tight_layout()
    plt.savefig('results.pdf',bbox_inches='tight')
    os.system('open results.pdf')
    # plt.show()
def main(argv):
    argc=len(argv)
    if(argc!=2):
        usage(argv)
        exit(0)
    plot_1d(argv[1])

if __name__ == '__main__':
    sys.exit(main(sys.argv))