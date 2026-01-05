#!python
import numpy as np 
import matplotlib.pyplot as plt 
import sys
from colored import fg, bg, attr
C_GREEN = fg('green')
C_RED = fg('red')
C_BLUE = fg('blue')
C_DEFAULT = attr('reset')
def usage(argv):
    basename = argv[0].split('/')
    basename = basename[len(basename)-1]
    print("======================"+basename+"=======================")
    print("Plot temperature and pressure field of HYDROTHERMAL")
    print("Zhikui Guo, 2018/10/26, GEOMAR")
    print("[""Example""]: "+C_RED + basename+C_BLUE +
          " dxdy100 3000.0")
    print("=======================================================")
    sys.exit(1)


def plotHT(prefix,time):
    fname_T=prefix+'_T_'+time+'.txt'
    fname_p=prefix+'_p_'+time+'.txt'
    fname_x=prefix+'_x.txt'
    fname_y=prefix+'_z.txt'
    x=np.loadtxt(fname_x)
    y=np.loadtxt(fname_y)
    xx,yy=np.meshgrid(x,y)
    T=np.loadtxt(fname_T)
    p=np.loadtxt(fname_p)
    fig,axs=plt.subplots(1,2,sharey=True)
    # fig=plt.figure()
    # ax=plt.gca()
    ax=axs[0]
    cs=ax.contourf(xx,yy,T)
    fig.colorbar(cs,ax=ax)

    ax=axs[1]
    cs=ax.contourf(xx,yy,p)
    fig.colorbar(cs,ax=ax)

    plt.show()


def main(argv):
    if(len(argv) != 3):
        usage(argv)
        exit(0)
    prefix=argv[1]
    time=argv[2]
    plotHT(prefix,time)

if __name__ == '__main__':
    sys.exit(main(sys.argv))