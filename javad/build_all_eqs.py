import sys,pickle
sys.path.insert(0, 'treebuilder')
from StringTemplate import StringTemplate

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

def floatcheck(n):
    try:
        n = ''.join([x for x in n if x not in ['$',',']])
        float(n)
        return n
    except:
        return -1
  
def populate_all_eqs(q,a):
    for i in range(len(q)):
        problem = q[i]
        problem = problem.strip().split(" ")
        for j,x in enumerate(problem):
            if len(x)==0:continue
            if x[-1] in [',','.','?']:
                problem[j] = x[:-1]+" "+x[-1]
        problem = ' '.join(problem)
        problem = " " + problem + " "

        question = [floatcheck(x) for x in problem.split(" ") if floatcheck(x)!=-1]
        answer = a[i]
        print(question)
        eqs = StringTemplate(question).equations
        good = []
        bad = []
        for e in eqs:
            e = e.toString()
            emod = e.replace('x',answer.strip())
            emod = emod.replace("=","==")
            try:
                if eval(emod):
                    good.append(e)
                else:
                    bad.append(e)
            except:
                bad.append(e)
        with open("eqs/"+str(i)+".eqs",'wb') as f:
            pickle.dump((good,bad),f)

if __name__=="__main__":
    #q, a = sys.argv[1:3]
    inp = sys.argv[1]
    q,a,e = parse_inp(inp)
    populate_all_eqs(q,a)
