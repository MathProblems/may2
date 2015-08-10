import sys
import random

def return_one(p,a,e,i):
    s = '{\n"iIndex": '+str(i)+',\n"sQuestion": "'+p.strip()+'",\n"lEquations": [\n"'+e.strip()+'"\n],\n"lSolutions": [ \n'+a.strip()+'\n ]\n}'
    return s

def floatcheck(x):
    try:
        x = ''.join([y for y in x if y != ','])
        return float(x)
    except:
        return False
def parse_inp(inp):
    q=[]
    a=[]
    e=[]
    with open(inp) as f:
        f = f.readlines()
        i=0
        while i<len(f):
            q.append(f[i])
            i+=1
            e.append(f[i])
            i+=1
            a.append(f[i])
            i+=1
    return (q,a,e)



if __name__=='__main__':
    q,aas,ees = parse_inp(sys.argv[1])

    print("[\n")
    for j,p in enumerate(q):
        a = str(float(aas[j]))
        e = str(ees[j])
        p = ' '.join([str(floatcheck(x)) if floatcheck(x) else x for x in p.split(" ")])
        if j+1 != len(q):
            print(return_one(p,a,e,j+1)+',')
        else:
            print(return_one(p,a,e,j+1)+"\n]")

    idx = list(range(len(q)))
    random.shuffle(idx)
    fold = len(q)//2
    for i in range(1):
        fn = "data_for_roy/indexes-1-fold-"+str(i)+".txt"
        thisfold = idx[i*fold:(i+1)*fold]
        with open(fn,'w') as f:
            for x in thisfold:
                f.write(str(x+1)+"\n")
    lastfold = idx[(i+1)*fold:]
    fn = "data_for_roy/indexes-1-fold-"+str(i+1)+".txt"
    with open(fn,'w') as f:
        for x in lastfold:
            f.write(str(x+1)+"\n")


