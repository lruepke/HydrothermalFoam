import numpy as np 
import matplotlib as plt

def hf_fixed(hfmin=0.05,hfmax=5):
    fpout=open('tmp_heatflux.txt','w')
    for i in range(0,ny):
        for j in range(0,nx):
            if(i==0 or i==(ny-1)):
                fpout.write('0 ')
            elif(j==0 or j==(nx-1)):
                fpout.write('0 ')
            elif((j>=40 and j<=49)):  # and (i>=40 and i<=49)
                fpout.write('%f '% (hfmax))
            else:
                fpout.write('%f '% (hfmin))
        fpout.write('\n')
    fpout.close()
def hf_gauss(hfmin=0.05,hfmax=5,c=500,xmin=50,xmax=8950,dx=100):
    fpout=open('tmp_heatflux.txt','w')
    x=np.linspace(xmin,xmax,90)
    y=np.linspace(xmin,xmax,90)
    bx=np.mean(x)
    by=np.mean(y)
    for i in range(0,len(y)):
        for j in range(0,len(x)):
            hf=(hfmax-hfmin)*np.exp(-((x[j]-bx)**2 + (y[i]-by)**2)/(2*c**2)) +hfmin;
            fpout.write('%f '% (hf))
        fpout.write('\n')
    fpout.close()

nx=90
ny=90
nz=30
pTop=300 #bar
Ttop=5 #deg. C
type_TopBoundary='-1' #-1: fixed T and fixed p; -1001: fixed p and inletoutlet T


# 1. generate slice 
fpout=open('tmp_slice.txt','w')
# IY=1
fpout.write('TOP\n')
for j in range(0,nz):
    fpout.write('%d*1\n'%(nx))
# 1<IY<NY
for i in range(1,ny-1):
    fpout.write('TOP\n')
    fpout.write('1 %d*%s 1\n'% (nx-2,type_TopBoundary))
    for j in range(0,nz-1):
        fpout.write('%d*1\n'%(nx))
# IY=NY
fpout.write('TOP\n')
for j in range(0,nz):
    fpout.write('%d*1\n'%(nx))
fpout.close()

fpout=open('tmp_top.txt','w')
# 2. generate top boundary condition
# 2.1 pressure
fpout.write('PRESSURE (bar)\n')
fpout.write('NODE\n')
for i in range(1,ny-1):
    for j in range(1,nx-1):
        fpout.write('     %d   %d   %d   %f\n'%(j+1,i+1,nz,pTop))
fpout.write('     %d   %d   %d   %d\n'%(0, 0, 0, 0))
# 2.2 temperature
fpout.write('TEMPERATURE (C)\n')
fpout.write('NODE\n')
for i in range(1,ny-1):
    for j in range(1,nx-1):
        fpout.write('     %d   %d   %d   %f\n'%(j+1,i+1,nz,Ttop))
fpout.write('     %d   %d   %d   %d\n'%(0, 0, 0, 0))
fpout.close()

# 2.3 heat flux on bottom
# hf_fixed()
hf_gauss()