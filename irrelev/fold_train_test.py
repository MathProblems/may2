import sys,os

datadir = "data_for_kush/"
folds = [x for x in os.listdir(datadir) if x[0]=='i']
test = [x for x in folds if str(sys.argv[1])+'.' in x][0]
folds.remove(test)

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


q,a,e = parse_inp(sys.argv[2])
train = []
for x in folds:
    train.extend(open(datadir+x).readlines())
train = [int(i)-1 for i in train]
test = [int(i)-1 for i in open(datadir+test).readlines()]
assert(len([x for x in train if x in test])==0)

trainq = [x for i,x in enumerate(q) if i in train]
traina = [x for i,x in enumerate(a) if i in train]
traine = [str(i)+'\n' for i,x in enumerate(e) if i in train]

testq= [x for i,x in enumerate(q) if i in test]
testa = [x for i,x in enumerate(a) if i in test]
teste = [str(i)+'\n' for i,x in enumerate(e) if i in test]
print(len(testq))

with open('data_for_kush/train'+sys.argv[1],'w') as f:
    for i in range(len(trainq)):
        f.write(trainq[i])
        f.write(traine[i])
        f.write(traina[i])
with open('data_for_kush/test'+str(sys.argv[1]),'w') as f:
    for i in range(len(testq)):
        f.write(testq[i])
        f.write(teste[i])
        f.write(testa[i])
