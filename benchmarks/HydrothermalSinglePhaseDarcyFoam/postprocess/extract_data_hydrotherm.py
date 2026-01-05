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
    print("[""Example""]: "+C_RED + basename+C_BLUE + " dx20")
    print("=======================================================")
    sys.exit(1)

TAG_COORD_X='X-Direction Node Coordinates'
TAG_COORD_Y='Y-Direction Node Coordinates'
TAG_COORD_Z='Z-Direction Node Coordinates'
TAG_TIME='Simulation time:'
TAG_FIELD='--- '
TAG_TEMPERATURE='--- Temperature Values ---'
TAG_COMPLETED='Simulation Completed'

# -------------------- helpers --------------------
def _has_field(data):
    return isinstance(data, dict) and bool(data.get('field'))

def _safe_extract_2d(fname):
    if not os.path.exists(fname):
        return None
    data = extract_Field_2D(fname)
    return data if _has_field(data) else None

def _safe_extract_3d(fname):
    if not os.path.exists(fname):
        return None
    data = extract_Field_3D(fname)
    return data if _has_field(data) else None

# -------------------- parsing --------------------
def extract_xyz(fname):
    result_ht={'x':[],'y':[],'z':[]}
    if(os.path.exists(fname)):
        ALLDATA=linecache.getlines(fname)
        for i in range(0,len(ALLDATA)):
            str_line=ALLDATA[i]
            if(TAG_COORD_X in str_line):
                result_ht['unit_x']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['x'].extend(coord_array); i=i+5
            if(TAG_COORD_Y in str_line):
                result_ht['unit_y']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['y'].extend(coord_array); i=i+5
            if(TAG_COORD_Z in str_line):
                result_ht['unit_z']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    if(TAG_TIME in ALLDATA[i]): break
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['z'].extend(coord_array); i=i+5
    for k in ('x','y','z'):
        if result_ht[k]!=[]: result_ht[k]=np.array(result_ht[k],dtype=float)
    return result_ht

def extract_field(ALLDATA,start,numZ,numY=1):
    i=start
    field=[[] for _ in range(numZ)]
    while(not ((TAG_TIME in ALLDATA[i]) | (TAG_FIELD in ALLDATA[i]))):
        str_array=np.array(ALLDATA[i].replace('\n','').split(' '))
        ind_num=(str_array!='')
        _ = np.array(str_array[ind_num],dtype=int)  # X indices, not used
        i=i+1
        if(TAG_COMPLETED in ALLDATA[i]) or (TAG_TIME in ALLDATA[i]) or (TAG_FIELD in ALLDATA[i]): break
        i0=i
        for i in range(i0,numZ+i0):
            str_array=np.array(ALLDATA[i].replace('\n','').split(' '))
            ind_num=(str_array!='')
            field_array=np.array(str_array[ind_num],dtype=float)
            field[int(field_array[0])-1].extend(field_array[1:])
        i=i+4
    return field,i

def extract_Field_2D(fname):
    result_ht={'t':[], 'field':[], 'x':[], 'y':[], 'z':[], 'Vx':[], 'Vz':[]}
    if(os.path.exists(fname)):
        ALLDATA=linecache.getlines(fname)
        for i in range(0,len(ALLDATA)):
            str_line=ALLDATA[i]
            if(TAG_COORD_X in str_line):
                result_ht['unit_x']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['x'].extend(coord_array); i=i+5
            if(TAG_COORD_Y in str_line):
                result_ht['unit_y']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['y'].extend(coord_array); i=i+5
            if(TAG_COORD_Z in str_line):
                result_ht['unit_z']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    if(TAG_TIME in ALLDATA[i]): break
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['z'].extend(coord_array); i=i+5
            if(TAG_TIME in str_line):
                t=float(str_line.split(TAG_TIME)[-1].split('(')[0])
                unit_t=str_line.split(TAG_TIME)[-1].split('(')[-1].split(')')[0]
                result_ht['unit_t']=unit_t
                result_ht['t'].append(t)
                i=i+2
                str_line=ALLDATA[i]
                if('velocity' in fname):
                    unit_v, Vx, Vz, end=extract_velocity(ALLDATA,i,len(result_ht['z']))
                    result_ht['Vx'].append(Vx); result_ht['Vz'].append(Vz); i=end
                else:
                    result_ht['unit_T']=str_line.split('(')[-1].split(')')[0]
                    field,end=extract_field(ALLDATA,i+2,len(result_ht['z']))
                    result_ht['field'].append(field); i=end
        linecache.clearcache()
    # finalize arrays
    for k in ('t','x','y','z'):
        if result_ht[k]!=[]: result_ht[k]=np.array(result_ht[k],dtype=float)
    for k in ('field','Vx','Vz'):
        if result_ht[k]!=[]: result_ht[k]=np.array(result_ht[k],dtype=float)
    return result_ht

def extract_velocity(ALLDATA,start,numZ):
    i=start-1
    Vx=[]; Vz=[]; unit_v=None
    while(not ((TAG_TIME in ALLDATA[i]))):
        i=i+1; str_line=ALLDATA[i]
        if('X Water Interstitial Velocity' in str_line):
            unit_v=str_line.split('(')[-1].split(')')[0]
            Vx,end=extract_field(ALLDATA,i+3,numZ); i=end-1
        if('Z Water Interstitial Velocity' in str_line):
            unit_v=str_line.split('(')[-1].split(')')[0]
            Vz,end=extract_field(ALLDATA,i+3,numZ); i=end-1
        if(TAG_COMPLETED in ALLDATA[i]) or (TAG_TIME in ALLDATA[i]): break
    return unit_v,Vx,Vz,i

def extract_Field_3D(fname):
    result_ht={'t':[], 'field':[], 'x':[], 'y':[], 'z':[], 'Vx':[], 'Vz':[]}
    if(os.path.exists(fname)):
        ALLDATA=linecache.getlines(fname)
        for i in range(0,len(ALLDATA)):
            str_line=ALLDATA[i]
            if(TAG_COORD_X in str_line):
                result_ht['unit_x']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['x'].extend(coord_array); i=i+5
            if(TAG_COORD_Y in str_line):
                result_ht['unit_y']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['y'].extend(coord_array); i=i+5
            if(TAG_COORD_Z in str_line):
                result_ht['unit_z']=str_line.split('(')[-1].split(')')[0]
                i=i+2
                while(ALLDATA[i]!='\n'):
                    if(TAG_TIME in ALLDATA[i]): break
                    str_array=np.array(ALLDATA[i+1].replace('\n','').split(' '))
                    ind_num=(str_array!='')
                    coord_array=np.array(str_array[ind_num],dtype=float)
                    result_ht['z'].extend(coord_array); i=i+5
            if(TAG_TIME in str_line):
                t=float(str_line.split(TAG_TIME)[-1].split('(')[0])  # np.float -> float
                unit_t=str_line.split(TAG_TIME)[-1].split('(')[-1].split(')')[0]
                result_ht['unit_t']=unit_t; result_ht['t'].append(t)
                i=i+2; str_line=ALLDATA[i]
                if('velocity' in fname):
                    unit_v,Vx,Vz,end=extract_velocity(ALLDATA,i,len(result_ht['z']))
                    result_ht['Vx'].append(Vx); result_ht['Vz'].append(Vz); i=end
                else:
                    result_ht['unit_T']=str_line.split('(')[-1].split(')')[0]
                    field,end=extract_field(ALLDATA,i+6,len(result_ht['z']))
                    field=np.array(field)
                    # original calc of field3d not used; we keep 2D-by-slab layout
                    result_ht['field'].append(field); i=end
        linecache.clearcache()
    for k in ('t','x','y','z'):
        if result_ht[k]!=[]: result_ht[k]=np.array(result_ht[k],dtype=float)
    for k in ('field','Vx','Vz'):
        if result_ht[k]!=[]: result_ht[k]=np.array(result_ht[k],dtype=float)
    return result_ht

# -------------------- writers (robust / optional H,S) --------------------
def write2file(TData,pData,prefix):
    x=TData['x']; z=TData['z']
    with open(prefix+'_x.txt','w') as fpx:
        for x0 in x: fpx.write('%E\n'%x0)
    with open(prefix+'_z.txt','w') as fpz:
        for z0 in z: fpz.write('%E\n'%z0)
    for idx,t in enumerate(TData['t']):
        p = pData['field'][idx]; T = TData['field'][idx]
        with open(f'{prefix}_p_{t}.txt','w') as fp_p, open(f'{prefix}_T_{t}.txt','w') as fp_T:
            for p_row, T_row in zip(p,T):
                for p0,T0 in zip(p_row,T_row):
                    fp_p.write('%e '%p0); fp_T.write('%e '%T0)
                fp_p.write('\n'); fp_T.write('\n')

def write2file_1D_vertical(TData,pData,hData,sData,prefix):
    """Vertical 1-D (len(x)==1): write z, T, p, and optionally h,S if present."""
    z=TData['z']
    has_h=_has_field(hData); has_s=_has_field(sData)
    for idx,t in enumerate(TData['t']):
        T = TData['field'][idx]; p = pData['field'][idx]
        h = hData['field'][idx] if has_h and idx < len(hData['field']) else None
        S = sData['field'][idx] if has_s and idx < len(sData['field']) else None

        # Flatten [numZ, 1] -> [numZ] if needed
        T1 = [row[0] if isinstance(row, (list, np.ndarray)) and np.size(row)==1 else row for row in T]
        p1 = [row[0] if isinstance(row, (list, np.ndarray)) and np.size(row)==1 else row for row in p]
        if h is not None:
            h1 = [row[0] if isinstance(row, (list, np.ndarray)) and np.size(row)==1 else row for row in h]
        if S is not None:
            S1 = [row[0] if isinstance(row, (list, np.ndarray)) and np.size(row)==1 else row for row in S]

        fname=f'{prefix}_T_p'
        if h is not None and S is not None:
            fname=f'{prefix}_T_p_h_S'
        with open(f'{fname}_{t}.txt','w') as fp:
            if h is not None and S is not None:
                fp.write('# z\tT\tp\th[kJ/kg]\tS\n')
                for z0,T0,p0,h0,S0 in zip(z,T1,p1,h1,S1):
                    fp.write(f'{z0:.6f}\t{T0:.6f}\t{p0:.6f}\t{h0:.6f}\t{S0:.6f}\n')
            else:
                fp.write('# z\tT\tp\n')
                for z0,T0,p0 in zip(z,T1,p1):
                    fp.write(f'{z0:.6f}\t{T0:.6f}\t{p0:.6f}\n')

def write2file_1D_horizontal(TData,pData,hData,sData,prefix):
    """Horizontal 1-D (len(z)==1): write x, T, p and optionally h,S if present."""
    x=TData['x']
    has_h=_has_field(hData); has_s=_has_field(sData)
    for idx,t in enumerate(TData['t']):
        T = TData['field'][idx][0]   # take the single z-layer
        p = pData['field'][idx][0]
        h = hData['field'][idx][0] if has_h and idx < len(hData['field']) else None
        S = sData['field'][idx][0] if has_s and idx < len(sData['field']) else None

        fname=f'{prefix}_T_p'
        if (h is not None) and (S is not None):
            fname=f'{prefix}_T_p_h_S'
        with open(f'{fname}_{t}.txt','w') as fp:
            if (h is not None) and (S is not None):
                fp.write('# x\tT\tp\th[kJ/kg]\tS\n')
                for x0,T0,p0,h0,S0 in zip(x,T,p,h,S):
                    fp.write(f'{x0:.6f}\t{T0:.6f}\t{p0:.6f}\t{h0:.6f}\t{S0:.6f}\n')
            else:
                fp.write('# x\tT\tp\n')
                for x0,T0,p0 in zip(x,T,p):
                    fp.write(f'{x0:.6f}\t{T0:.6f}\t{p0:.6f}\n')

def write2vtk_vel(TData,pData,VData,hData,sData,prefix):
    path_result=prefix+'_vtk'; os.system('mkdir '+path_result)
    x=TData['x']; z=TData['z']
    has_h=_has_field(hData); has_s=_has_field(sData)
    for idx,t in enumerate(TData['t']):
        p = pData['field'][idx]; T = TData['field'][idx]
        Vx= VData['Vx'][idx]; Vz= VData['Vz'][idx]
        fields=[('p',p),('T',T)]
        if has_h and idx<len(hData['field']): fields.append(('h',hData['field'][idx]))
        if has_s and idx<len(sData['field']): fields.append(('S',sData['field'][idx]))
        with open(f'{path_result}/res_{int(t)}.vtk','w') as fpout:
            fpout.write('# vtk DataFile Version 2.0\nHYDROTHERMAL '+prefix+' T p [h S]\nASCII\n')
            fpout.write('DATASET RECTILINEAR_GRID\n')
            fpout.write('DIMENSIONS %d %d %d\n'%(len(x),len(z),1))
            fpout.write('X_COORDINATES %d double\n'%len(x)); fpout.write(' '.join(f'{v:.5E}' for v in x)+'\n')
            fpout.write('Y_COORDINATES %d double\n'%len(z)); fpout.write(' '.join(f'{v:.5E}' for v in z)+'\n')
            fpout.write('Z_COORDINATES 1 double\n0\n')
            fpout.write('POINT_DATA %d\n'%(len(x)*len(z)))
            # scalars
            for name,field in fields:
                fpout.write(f'SCALARS {name} float\nLOOKUP_TABLE default\n')
                for row in field:
                    for val in row: fpout.write(f'{val:e} ')
                    fpout.write('\n')
                fpout.write('\n')
            # vectors
            fpout.write('VECTORS Velocity float\n')
            for Vx_row, Vz_row in zip(Vx,Vz):
                for Vx0,Vz0 in zip(Vx_row,Vz_row):
                    fpout.write(f'{Vx0:e} {Vz0:e} 0 ')
                fpout.write('\n')

def write2vtk(TData,pData,hData,sData,prefix):
    path_result=prefix+'_vtk'; os.system('mkdir '+path_result)
    x=TData['x']; z=TData['z']; y=TData['y']
    has_h=_has_field(hData); has_s=_has_field(sData)
    for idx,t in enumerate(TData['t']):
        p = pData['field'][idx]; T = TData['field'][idx]
        fields=[('p',p),('T',T)]
        if has_h and idx<len(hData['field']): fields.append(('h',hData['field'][idx]))
        if has_s and idx<len(sData['field']): fields.append(('S',sData['field'][idx]))
        with open(f'{path_result}/res_{int(t)}.vtk','w') as fpout:
            fpout.write('# vtk DataFile Version 2.0\nHYDROTHERMAL '+prefix+' T p [h S]\nASCII\n')
            fpout.write('DATASET RECTILINEAR_GRID\n')
            fpout.write('DIMENSIONS %d %d %d\n'%(len(x),len(z),len(y)))
            fpout.write('X_COORDINATES %d double\n'%len(x)); fpout.write(' '.join(f'{v:.5E}' for v in x)+'\n')
            fpout.write('Y_COORDINATES %d double\n'%len(z)); fpout.write(' '.join(f'{v:.5E}' for v in z)+'\n')
            fpout.write('Z_COORDINATES %d double\n'%len(y)); fpout.write(' '.join(f'{v:.5E}' for v in y)+'\n')
            fpout.write('POINT_DATA %d\n'%(len(x)*len(z)*len(y)))
            for name,field in fields:
                fpout.write(f'SCALARS {name} float\nLOOKUP_TABLE default\n')
                for k in range(0,len(y)):
                    for j in range(0,len(z)):
                        for i in range(0,len(x)):
                            fpout.write('%e '%(field[j][i+k*len(x)]))
                        fpout.write('\n')
                fpout.write('\n')

# -------------------- main --------------------
def main(argv):
    if(len(argv) != 2):
        usage(argv); exit(0)

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
        hData=_safe_extract_2d(fname_h)  # may be None
        sData=_safe_extract_2d(fname_S)  # may be None
        write2file_1D_vertical(TData,pData,hData,sData,fname_T.split('.')[-1])

    elif(len(xyz['z'])==1):
        print('Horizontal 1D case')
        TData=extract_Field_2D(fname_T)
        pData=extract_Field_2D(fname_p)
        hData=_safe_extract_2d(fname_h)
        sData=_safe_extract_2d(fname_S)
        write2file_1D_horizontal(TData,pData,hData,sData,fname_T.split('.')[-1])

    elif(len(xyz['y'])==1):
        print('2D case')
        TData=extract_Field_2D(fname_T)
        pData=extract_Field_2D(fname_p)
        hData=_safe_extract_2d(fname_h)
        sData=_safe_extract_2d(fname_S)
        if(os.path.exists(fname_V)):
            VData=extract_Field_2D(fname_V)
            write2vtk_vel(TData,pData,VData,hData,sData,fname_T.split('.')[-1])
        else:
            write2vtk(TData,pData,hData,sData,fname_T.split('.')[-1])

    else:
        print('3D case')
        TData=extract_Field_3D(fname_T)
        pData=extract_Field_3D(fname_p)
        hData=_safe_extract_3d(fname_h)
        sData=_safe_extract_3d(fname_S)
        if(os.path.exists(fname_V)):
            # 3D velocity writing not implemented; still write scalars
            write2vtk(TData,pData,hData,sData,fname_T.split('.')[-1])
        else:
            write2vtk(TData,pData,hData,sData,fname_T.split('.')[-1])

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
