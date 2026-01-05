#!python
import linecache
import sys 

def setEmptyPatch(patchName,fname_boundary='constant/polyMesh/boundary'):
    ALLDATA=linecache.getlines(fname_boundary)
    linecache.clearcache()
    start=0
    end=0
    for i in range(0,len(ALLDATA)):
        if(patchName in ALLDATA[i].replace('\n','')):
            start=i
            for i in range(start,start+100):
                if('}' in ALLDATA[i]):
                    end=i
                    break
    for i in range(start,end):
        if('type' in ALLDATA[i]):
            ALLDATA[i]=ALLDATA[i].replace('patch','empty')
    fpout=open(fname_boundary,'w')
    for str_line in ALLDATA:
        fpout.write('%s'% str_line)
    fpout.close()

def main(argv):
    if(len(argv)!=2):
        print('useage: ./setEmptyPatch.py frontAndBack')
        exit(0)
    patchName=argv[1]
    setEmptyPatch(patchName)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
