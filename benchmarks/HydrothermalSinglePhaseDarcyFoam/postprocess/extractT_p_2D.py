#!python
import numpy as np 
import linecache
import matplotlib 
import sys
import os

from colored import fg, bg, attr
C_GREEN = fg('green')
C_RED = fg('red')
C_BLUE = fg('blue')
C_DEFAULT = attr('reset')
def usage(argv):
    basename = argv[0].split('/')
    basename = basename[len(basename)-1]
    print("======================"+basename+"=======================")
    print("Extract results of HYDROTHERMAL")
    print("Zhikui Guo, 2018/1/8, GEOMAR")
    print("[""Example""]: "+C_RED + basename+C_BLUE +
          " dx20")
    print("=======================================================")
    sys.exit(1)

TAG_COORD_X='X-Direction Node Coordinates'
TAG_COORD_Y='Y-Direction Node Coordinates'
TAG_COORD_Z='Z-Direction Node Coordinates'
TAG_TIME='Simulation time:'
TAG_FIELD='--- '
TAG_TEMPERATURE='--- Temperature Values ---'
TAG_COMPLETED='Simulation Completed'
def extract_xyz(fname):
    result_ht={}
    result_ht['x']=[]
    result_ht['y']=[]
    result_ht['z']=[]
    if(os.path.exists(fname)):
        ALLDATA=linecache.getlines(fname)
        for i in range(0,len(ALLDATA)):
            str_line=ALLDATA[i]
            # 1. x coordinate
            if(TAG_COORD_X in str_line):
                result_ht['unit_x']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['x'].extend(coord_array)
                    i=i+5
            # 1. x coordinate
            if(TAG_COORD_Y in str_line):
                result_ht['unit_y']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['y'].extend(coord_array)
                    i=i+5
            # 2. z coordinate
            if(TAG_COORD_Z in str_line):
                result_ht['unit_z']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    if(TAG_TIME in ALLDATA[i]):
                        break
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['z'].extend(coord_array)
                    i=i+5
    if(result_ht['x']!=[]):
        result_ht['x']=np.array(result_ht['x'],dtype=float)
    if(result_ht['y']!=[]):
        result_ht['y']=np.array(result_ht['y'],dtype=float)
    if(result_ht['z']!=[]):
        result_ht['z']=np.array(result_ht['z'],dtype=float)
    return result_ht
def extract_field(ALLDATA,start,numZ,numY=1):
    i=start
    field=[]
    for j in range(0,numZ):
        field.append([])
    while(not ((TAG_TIME in ALLDATA[i]) | (TAG_FIELD in ALLDATA[i]))):
        str_array=np.array(ALLDATA[i].replace('\n','').split(' '))
        ind_num=(str_array!='')
        ind_X=np.array(str_array[ind_num],dtype=int)
        i=i+1
        if(TAG_COMPLETED in ALLDATA[i]):
            break
        if(TAG_TIME in ALLDATA[i]):
            break
        if(TAG_FIELD in ALLDATA[i]):
            break
        i0=i
        for i in range(i0,numZ+i0):
            str_array=np.array(ALLDATA[i].replace('\n','').split(' '))
            ind_num=(str_array!='')
            field_array=np.array(str_array[ind_num],dtype=float)
            field[int(field_array[0])-1].extend(field_array[1:])
        # print(str_array)
        i=i+4
    # print(i,field)
    return field,i
def extract_Field_2D(fname):
    result_ht={}
    result_ht['t']=[]
    result_ht['field']=[]
    result_ht['x']=[]
    result_ht['y']=[]
    result_ht['z']=[]
    result_ht['Vx']=[]
    result_ht['Vz']=[]
    if(os.path.exists(fname)):
        ALLDATA=linecache.getlines(fname)
        for i in range(0,len(ALLDATA)):
            str_line=ALLDATA[i]
            # 1. x coordinate
            if(TAG_COORD_X in str_line):
                result_ht['unit_x']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['x'].extend(coord_array)
                    i=i+5
            # 1. x coordinate
            if(TAG_COORD_Y in str_line):
                result_ht['unit_y']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['y'].extend(coord_array)
                    i=i+5
            # 2. z coordinate
            if(TAG_COORD_Z in str_line):
                result_ht['unit_z']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    if(TAG_TIME in ALLDATA[i]):
                        break
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['z'].extend(coord_array)
                    i=i+5
                # print(result_ht['z'])
            # 3. extract field for every write time
            if(TAG_TIME in str_line):
                t=float(str_line.split(TAG_TIME)[-1].split('(')[0])
                unit_t=str_line.split(TAG_TIME)[-1].split('(')[-1].split(')')[0]
                result_ht['unit_t']=unit_t
                result_ht['t'].append(t)
                # print(result_ht['t'])
                i=i+2
                str_line=ALLDATA[i]
                if('velocity' in fname):
                    unit_v, Vx, Vz, end=extract_velocity(ALLDATA,i,len(result_ht['z']))
                    result_ht['Vx'].append(Vx)
                    result_ht['Vz'].append(Vz)
                    i=end
                else:
                    result_ht['unit_T']=str_line.split('(')[-1].split(')')[0]
                    # print(result_ht['unit_T'])
                    field,end=extract_field(ALLDATA,i+2,len(result_ht['z']))
                    result_ht['field'].append(field)
                    i=end
                # print(field)
        linecache.clearcache()
    else:
        print(fname+' does not exist')
    if(result_ht['t']!=[]):
        result_ht['t']=np.array(result_ht['t'],dtype=float)
    if(result_ht['field']!=[]):
        result_ht['field']=np.array(result_ht['field'],dtype=float)
    if(result_ht['Vx']!=[]):
        result_ht['Vx']=np.array(result_ht['Vx'],dtype=float)
    if(result_ht['Vz']!=[]):
        result_ht['Vz']=np.array(result_ht['Vz'],dtype=float)
    if(result_ht['x']!=[]):
        result_ht['x']=np.array(result_ht['x'],dtype=float)
    if(result_ht['z']!=[]):
        result_ht['z']=np.array(result_ht['z'],dtype=float)
    return result_ht
def extract_velocity(ALLDATA,start,numZ):
    i=start-1
    Vx=[]
    Vz=[]
    while(not ((TAG_TIME in ALLDATA[i]))):
        i=i+1
        str_line=ALLDATA[i]
        if('X Water Interstitial Velocity' in str_line):
            unit_v=str_line.split('(')[-1].split(')')[0]
            # print(unit_v, str_line)
            Vx,end=extract_field(ALLDATA,i+3,numZ)
            i=end-1
        if('Z Water Interstitial Velocity' in str_line):
            unit_v=str_line.split('(')[-1].split(')')[0]
            # print(unit_v, str_line)
            Vz,end=extract_field(ALLDATA,i+3,numZ)
            i=end-1
        if(TAG_COMPLETED in ALLDATA[i]):
            break
        if(TAG_TIME in ALLDATA[i]):
            break
    return unit_v,Vx, Vz, i
def extract_Field_3D(fname):
    result_ht={}
    result_ht['t']=[]
    result_ht['field']=[]
    result_ht['x']=[]
    result_ht['y']=[]
    result_ht['z']=[]
    result_ht['Vx']=[]
    result_ht['Vz']=[]
    if(os.path.exists(fname)):
        ALLDATA=linecache.getlines(fname)
        for i in range(0,len(ALLDATA)):
            str_line=ALLDATA[i]
            # 1. x coordinate
            if(TAG_COORD_X in str_line):
                result_ht['unit_x']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['x'].extend(coord_array)
                    i=i+5
            # 2. x coordinate
            if(TAG_COORD_Y in str_line):
                result_ht['unit_y']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['y'].extend(coord_array)
                    i=i+5
            # 3. z coordinate
            if(TAG_COORD_Z in str_line):
                result_ht['unit_z']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    if(TAG_TIME in ALLDATA[i]):
                        break
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['z'].extend(coord_array)
                    i=i+5
                # print(result_ht['z'])
            # 3. extract field for every write-time
            if(TAG_TIME in str_line):
                t=np.float(str_line.split(TAG_TIME)[-1].split('(')[0])
                unit_t=str_line.split(TAG_TIME)[-1].split('(')[-1].split(')')[0]
                result_ht['unit_t']=unit_t
                result_ht['t'].append(t)
                # print(result_ht['t'])
                i=i+2
                str_line=ALLDATA[i]
                if('velocity' in fname):
                    unit_v, Vx, Vz, end=extract_velocity(ALLDATA,i,len(result_ht['z']))
                    result_ht['Vx'].append(Vx)
                    result_ht['Vz'].append(Vz)
                    i=end
                else:
                    result_ht['unit_T']=str_line.split('(')[-1].split(')')[0]
                    # print(result_ht['unit_T'])
                    field,end=extract_field(ALLDATA,i+6,len(result_ht['z']))
                    field=np.array(field)
                    field3d=field.reshape((len(result_ht['x']),len(result_ht['z']),len(result_ht['y'])))
                    result_ht['field'].append(field)
                    i=end
                # print(field)
        linecache.clearcache()
    else:
        print(fname+' does not exist')
    if(result_ht['t']!=[]):
        result_ht['t']=np.array(result_ht['t'],dtype=float)
    if(result_ht['field']!=[]):
        result_ht['field']=np.array(result_ht['field'],dtype=float)
    if(result_ht['Vx']!=[]):
        result_ht['Vx']=np.array(result_ht['Vx'],dtype=float)
    if(result_ht['Vz']!=[]):
        result_ht['Vz']=np.array(result_ht['Vz'],dtype=float)
    if(result_ht['x']!=[]):
        result_ht['x']=np.array(result_ht['x'],dtype=float)
    if(result_ht['z']!=[]):
        result_ht['z']=np.array(result_ht['z'],dtype=float)
    return result_ht

def write2file(TData,pData,prefix):
    x=TData['x']
    z=TData['z']
    # write x
    fpout=open(prefix+'_x'+'.txt','w')
    for x0 in x:
        fpout.write('%E\n'% x0)
    fpout.close()
    # write z
    fpout=open(prefix+'_z'+'.txt','w')
    for z0 in z:
        fpout.write('%E\n'% z0)
    fpout.close()
    for t,p,T in zip(TData['t'],pData['field'],TData['field']):
        fpout_p=open(prefix+'_p_'+str(t)+'.txt','w')
        fpout_T=open(prefix+'_T_'+str(t)+'.txt','w')
        for p_row, T_row in zip(p,T):
            for p0, T0 in zip(p_row,T_row):
                fpout_p.write('%e '% (p0))
                fpout_T.write('%e '% (T0))
            fpout_p.write('\n')
            fpout_T.write('\n')
        fpout_p.close()
        fpout_T.close()
def write2vtk_vel(TData,pData,VData,hData,sData,prefix):
    # create folder
    path_result=prefix+'_vtk'
    os.system('mkdir '+path_result)
    x=TData['x']
    z=TData['z']
    for t,p,T,Vx,Vz in zip(TData['t'],pData['field'],TData['field'],VData['Vx'],VData['Vz']):
        fpout=open(path_result+'/res_'+str(int(t))+'.vtk','w')
        fpout.write('# vtk DataFile Version 2.0\n')
        fpout.write('HYDROTHERMAL '+prefix+' T and p\n')
        fpout.write('ASCII\n')
        fpout.write('DATASET RECTILINEAR_GRID\n')
        fpout.write('DIMENSIONS %d %d %d\n'% (len(x),len(z),1))
        fpout.write('X_COORDINATES %d double\n'% (len(x)))
        for i in range(0,len(x)):
            fpout.write('%.5E '% (x[i]))
        fpout.write('\nY_COORDINATES %d double\n'% (len(z)))
        for i in range(0,len(z)):
            fpout.write('%.5E '% (z[i]))
        fpout.write('\nZ_COORDINATES 1 double\n')
        fpout.write('0\n')
        fpout.write('POINT_DATA %d\n'% (len(x)*len(z)))
        # temperature
        for field_, name_field_ in zip([p,T,h, S], ['p','T','h','S']):
            fpout.write('SCALARS %s float\n'%(name_field_))
            fpout.write('LOOKUP_TABLE default\n')
            for T_row in field_:
                for T0 in T_row:
                    fpout.write('%e '% (T0))
                fpout.write('\n')
            fpout.write('\n')
        # Velocity
        fpout.write('VECTORS Velocity float\n')
        for Vx_row, Vz_row in zip(Vx, Vz):
            for Vx0, Vz0 in zip(Vx_row, Vz_row):
                fpout.write('%e %e %e'% (Vx0, Vz0, 0))
            fpout.write('\n')
        fpout.close()
def write2vtk(TData,pData,hData,sData,prefix):
    # create folder
    path_result=prefix+'_vtk'
    os.system('mkdir '+path_result)
    x=TData['x']
    z=TData['z']
    y=TData['y']
    for t,p,T,h,S in zip(TData['t'],pData['field'],TData['field'],hData['field'],sData['field']):
        fpout=open(path_result+'/res_'+str(int(t))+'.vtk','w')
        fpout.write('# vtk DataFile Version 2.0\n')
        fpout.write('HYDROTHERMAL '+prefix+' T and p\n')
        fpout.write('ASCII\n')
        fpout.write('DATASET RECTILINEAR_GRID\n')
        fpout.write('DIMENSIONS %d %d %d\n'% (len(x),len(z),len(y)))
        fpout.write('X_COORDINATES %d double\n'% (len(x)))
        for i in range(0,len(x)):
            fpout.write('%.5E '% (x[i]))
        fpout.write('\nY_COORDINATES %d double\n'% (len(z)))
        for i in range(0,len(z)):
            fpout.write('%.5E '% (z[i]))
        fpout.write('\nZ_COORDINATES %d double\n'% (len(y)))
        for i in range(0,len(y)):
            fpout.write('%.5E '% (y[i]))
        fpout.write('\nPOINT_DATA %d\n'% (len(x)*len(z)*len(y)))
        # write field: T,p, h,S
        for field_, name_field_ in zip([p,T,h, S], ['p','T','h','S']):
            fpout.write('SCALARS %s float\n'%(name_field_))
            fpout.write('LOOKUP_TABLE default\n')
            for k in range(0,len(y)):
                for j in range(0,len(z)):
                    for i in range(0,len(x)):
                        fpout.write('%e '% (field_[j][i+k*len(x)]))
                    fpout.write('\n')
            fpout.write('\n')
        fpout.close()
def write2file_1D_V(TData,pData,prefix):
    z=TData['z']
    for t,p,T in zip(TData['t'],pData['field'],TData['field']):
        fpout=open(prefix+'_T_p_'+str(t)+'.txt','w')
        fpout.write('# x\tT\tp\n')
        for z0, T0, p0 in zip(z,T,p):
            fpout.write('%.6f\t%.6f\t%.6f\n'% (z0,T0,p0))
        fpout.close()
def write2file_1D_H(TData,pData,hData,sData,prefix):
    x=TData['x']
    for t,p,T,h,S in zip(TData['t'],pData['field'],TData['field'],hData['field'],sData['field']):
        fpout=open(prefix+'_T_p_h_S_'+str(t)+'.txt','w')
        fpout.write('# x\tT\tp\th[kJ/kg]\tS\n')
        for x0, T0, p0,h0,S0 in zip(x,T[0],p[0],h[0],S[0]):
            fpout.write('%.6f\t%.6f\t%.6f\t%.6f\t%.6f\n'% (x0,T0,p0,h0,S0))
        fpout.close()
# ------------extract data-------------------
def main(argv):
    if(len(argv) != 2):
        usage(argv)
        exit(0)
    extname='.%s'%(argv[1]) if (argv[1]!="") else ""
    fname_T='Out_temperature'+extname
    fname_p='Out_pressure'+extname
    fname_V='Out_velocity'+extname
    fname_h='Out_enthalpy'+extname
    fname_S='Out_saturation'+extname
    xyz=extract_xyz(fname_T)
    if(len(xyz['x'])==1):
        print('Vertical 1D case')
        TData=extract_Field_2D(fname_T)
        pData=extract_Field_2D(fname_p)
        write2file_1D_V(TData,pData,fname_T.split('.')[-1])
    elif(len(xyz['z'])==1):
        print('Horizontal 1D case')
        TData=extract_Field_2D(fname_T)
        pData=extract_Field_2D(fname_p)
        hData=extract_Field_2D(fname_h)
        sData=extract_Field_2D(fname_S)
        write2file_1D_H(TData,pData,hData,sData,fname_T.split('.')[-1])
    elif(len(xyz['y'])==1):
        print('2D case')
        TData=extract_Field_2D(fname_T)
        pData=extract_Field_2D(fname_p)
        hData=extract_Field_2D(fname_h)
        sData=extract_Field_2D(fname_S)
        if(os.path.exists(fname_V)):
            VData=extract_Field_2D(fname_V)
            write2vtk_vel(TData,pData,VData,hData,sData,fname_T.split('.')[-1])
        else:
            write2vtk(TData,pData,hData,sData,fname_T.split('.')[-1])
        # write2file(TData,pData,fname_T.split('.')[-1])
    else:
        print('3D case')
        TData=extract_Field_3D(fname_T)
        pData=extract_Field_3D(fname_p)
        if(os.path.exists(fname_V)):
            # VData=extract_Field_3D(fname_V)
            # write2vtk_vel(TData,pData,VData,fname_T.split('.')[-1])
            write2vtk(TData,pData,fname_T.split('.')[-1])
        else:
            write2vtk(TData,pData,fname_T.split('.')[-1])
    # ...

if __name__ == '__main__':
    sys.exit(main(sys.argv))