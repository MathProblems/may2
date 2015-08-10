import signal
import sys
import json
import jsonrpclib
import makesets
import pickle
from random import randint

LEN = None
LEN2 = None

class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()

def cleannum(n):
    n = ''.join([x for x in n if x.isdigit() or x=='.' or x=='x' or x=='x*'])
    return n

def kill(signum, frame):
    raise Exception("end of time")

def training(trips,problem,story,target,sets):
    #this function take the trips and creates positive and negative training instances from them
    
    texamples = {x:([],[]) for x in ["+","*",'/','-','=']}
    for op,a,b in trips:
        if op == '=':
            vec = makesets.eqvector(a,b,problem,story,target,sets)
        else:
            vec = makesets.vector(a,b,problem,story,target)
        texamples[op][0].append(vec)

    return texamples


def make_eq(q,a,equations):
    bigtexamples = {x:([],[]) for x in ["+","*",'/','-','=']}
    wps = q #open(q).readlines()
    answs = a #open(a).readlines()

    for k in range(len(wps)):
        if k%3==2:continue
        eqs = get_k_eqs(equations[k])
        answers = [x[1] for x in eqs if x[0]==1]
        answers = [x for x in answers if x.split()[-2]=='=']
        answers = [x for x in answers if x.split()[-1]=='x']
        if answers == []: continue
        answers = list(set(answers))


        #First preprocessing, tokenize slightly
        problem = wps[k]#.lower()
        problem = problem.strip().split(" ")
        for i,x in enumerate(problem):
            if len(x)==0:continue
            if x[-1] in [',','.','?']:
                problem[i] = x[:-1]+" "+x[-1]
        problem = ' '.join(problem)
        problem = " " + problem + " "
        print(k)
        print(problem)

        #make story
        story = nlp.parse(problem)
        sets = makesets.makesets(story['sentences'])
        i = 0

        xidx = [i for i,x in enumerate(sets) if x[1].num=='x']
        if not xidx:
            print("NO X WHY");continue


        numlist = [(cleannum(v.num),v) for k,v in sets]
        numlist = [x for x in numlist if x[0]!='']
        allnumbs = {str(k):v for k,v in numlist}
        objs = {k:(0,v) for k,v in numlist}
        print(objs.items())
        consts = [x for x in answers[0].split(" ") if x not in ['(',')','+','-','/','*','=',]]
        present = [x for x in consts if x in objs]
        if present!=consts: print(present,consts);print("missing thing");continue

        #simpleanswers = []
        #for x in answers:
        #    try:
        #        x1 = x[1].strip().split(" ")
        #        if x[-2]=='=' and x[-1]=='x':
        #            simplenaswers.append(x)
        #    except:
        #        pass
        #if simpleanswers:
        #    answers = simpleanswers

        #ri = randint(0,len(answers)-1)
        #if answers == []:
        #    continue
        #answers = [answers[ri]]
        for j,eq in enumerate(answers):
            trips = []
            print(j,eq)
            l,r = [x.strip().split(' ') for x in eq.split('=')]
            
            target = 'x'
            target = (target,objs[target])

            #find innermost parens?
            sides = []
            for i,compound in enumerate([l,r]):
                while len(compound)>1:
                    if "(" in compound:
                        rpidx = (len(compound) - 1) - compound[::-1].index('(')
                        lpidx = rpidx+compound[rpidx:].index(")")
                        subeq = compound[rpidx+1:lpidx]
                        substr = "("+''.join(subeq)+")"
                        compound = compound[:rpidx]+[substr]+compound[lpidx+1:]
                    else:
                        subeq = compound[0:3]
                        substr = "("+''.join(subeq)+")"
                        compound = [substr]+compound[3:]
                    if True:
                        p,op,e = subeq
                        p = objs[p]
                        e = objs[e]
                        op = op.strip()
                        trips.append((op,p,e))
                        pute = (0,makesets.combine(p[1],e[1],op))
                        objs[substr]=pute
                    if pute == -1:
                        exit()
            t = training(trips,problem,story,target,sets)
            for op in t:
                bigtexamples[op][0].extend(t[op][0])
                bigtexamples[op][1].extend(t[op][1])
    pickle.dump(bigtexamples,open('data/3.local.training','wb'))



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

def get_k_eqs(i,k=100,g=False,a=False):
    i = int(i)
    if int(i) >= LEN and i < LEN2:
        i = i - LEN
        eqsdir = eq2+eq2[:-1]+".out/"
    elif i >= LEN2:
        i = i - LEN2
        eqsdir = eq3+eq3[:-1]+".out/"
    else:
        eqsdir = eq1+eq1[:-1]+".out/"

    #if a==True:
    #    eqsdir = eq3+eq3[:-1]+'.out'
    digit = "{0:0=3d}".format(int(i))
    exprs = []
    with open(eqsdir+"/q"+digit+".txt.out") as f:
        f = f.readlines()[3:-1]
        j = 0
        while j<k:
            if j>=len(f): break
            line = f[j]
            line = line.split(" | ")
            good = line[0].split(": ")[1]
            exp = line[6]
            if '/' in exp or "*" in exp:
                j+=1;k+=1;continue
            for s in ['(',')','+','-','*','/','=']:
                exp = exp.replace(s,' '+s+' ')
            exp = exp.replace('  ',' ').strip()
            if g:
                cons = int(line[3])
                if cons == 0:
                    cons = 1
                else:
                    cons = 1/(cons+1)
                if a:
                    answ = line[5]
                    exprs.append((int(good),exp,cons,answ))
                else:
                    exprs.append((int(good),exp,cons))

            else:
                exprs.append((int(good),exp))
            j+=1
    return exprs

eq2 = 'DS1/'
eq3 = 'DS2/'
eq1 = 'DS3/'

if __name__=="__main__":
    #q, a = sys.argv[1:3]
    #eqsdir = sys.argv[2]
    #makesets.FOLD = sys.argv[1][-1]
    q,a,e = parse_inp(eq1+'formatted.txt')
    q2,a2,e2 = parse_inp(eq2+'formatted.txt')
    q3,a3,e3 = parse_inp(eq3+'formatted.txt')
    LEN = len(q)
    q = q + q2
    LEN2 = len(q)
    a = a + a2 + a3
    e = [i for i in range(len(q))]+[LEN2+i for i in range(len(q3))]
    q = q+q3


    make_eq(q,a,e)


