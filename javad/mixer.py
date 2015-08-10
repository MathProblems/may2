import sys
from shutil import copy
#this mixes ixl and emnlp reduced

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


ixl = parse_inp("IXL.curated.txt")
er = parse_inp("emnlp.reduced.kushformat.txt")
good = [[],[],[]]
j = 255
for i,q in enumerate(ixl[0]):
    if q not in er[0]:
        digit = "{0:0=3d}".format(int(i))
        good[0].append(ixl[0][i])
        good[1].append(ixl[1][i])
        good[2].append(ixl[2][i])
        src = "data.IXL.curated/q"+str(digit)+".txt.out"
        dest = "data.emnlp.reduced.plus/q"+str(j)+".txt.out"
        j+=1 
        copy(src,dest)

for i in range(len(good[0])):
    print(good[0][i].strip())
    print(good[2][i].strip())
    print(good[1][i].strip())
