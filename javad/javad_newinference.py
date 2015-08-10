import signal
import sys
import json
import jsonrpclib
import makesets
import pickle
from random import randint
import javad_train_local #import get_k_eqs
from functools import reduce
sys.path.insert(0, '/Users/rikka/libsvm-3.18/python')
from svmutil import *


class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()

def cleannum(n):
    n = ''.join([x for x in n if x.isdigit() or x=='.' or x=='x' or x=='x*'])
    return n
multi = None
glob = None

def make_eq(q,a,equations):
    wps = q #open(q).readlines()
    answs = a #open(a).readlines()
    right = 0
    wrong = 0
    #IRR = open("output_relevant.txt").readlines()
    #IRR = [x.strip().split(" ") for x in IRR]
    #IRR = [[y.split(",")[1:] for y in x] for x in IRR]

    for k in range(len(wps)):
        answers = javad_train_local.get_k_eqs(equations[k],g=True,a=True)
        answers = [x for x in answers if x[1].split()[-2]=='=']
        answers = [x for x in answers if x[1].split()[-1]=='x' or x[1].split()[-3]=='x']

        if answers == []: continue
        seeneq = []
        seen = []
        for x in answers:
            if x[1] not in seeneq:
                seen.append(x)
                seeneq.append(x[1])
        answers = seen
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
        print(problem)

        #irrelev = IRR[k]
        #if len(set([x[1] for x in irrelev]))==1:
        #    irrelev = False
        #make story
        story = nlp.parse(problem)
        sets = makesets.makesets(story['sentences'])
        i = 0

        ######
        for x in sets:
            x[1].details()
        #continue

        xidx = [i for i,x in enumerate(sets) if x[1].num=='x']
        if not xidx:
            print("NO X WHY");continue

        #TODO look for 2 xes
        xidx = xidx[0]


        numlist = [(cleannum(v.num),v) for k,v in sets]
        numlist = [x for x in numlist if x[0]!='']
        allnumbs = {str(k):v for k,v in numlist}
        objs = {k:(0,v) for k,v in numlist}
        print(objs.items())
        consts = [x for x in answers[0][1].split(" ") if x not in ['(',')','+','-','/','*','=','x']]
        present = [x for x in consts if x in objs]
        if consts!=present: print(present,consts);print("missing thing");continue
        #if len([x for x in objs if x not in consts])>0: print("missing thing");continue
        scores = []

                ############# THING
        '''
        numlist2 = [x[0] for x in numlist if x[0] != 'x']
        ok = True
        if len(numlist2)==2:
            a = float(numlist2[0])
            b = float(numlist2[1])
            if a < b:
                answers = [x for x in answers if (x[1].split()[-1]=='x' and x[1].split()[1]=='+') or (x[1].split()[1]=='-' and x[1].split()[2]=='x')]
                ok = False
        if ok:
            answers = [x for x in answers if x[1].split()[-1]=='x']

        thing = problem.split(".")[-1]
        if ' how ' in problem:
            problem = problem.split(" how ")[-1]
        thing = ''.join([x.lower() for x in thing if x.isalpha() or x==' '])
        thing = [x for x in thing.split(" ") if x in ['more','farther','taller','longer','less']]
        if len(thing)>0:
            numlist2 = [x[0] for x in numlist if x[0] != 'x']
            print(numlist2)
            if len(numlist2)==2:
                print("THING HAPPENING")
                a = numlist2[0]
                b = numlist2[1]
                print(a,b)
                an = answs[k].strip()
                a = float(a)
                b = float(b)
                if a<b:
                    answers = b - a # str(a)+" + "+str(an)+" == "+str(b)
                else:
                    answers = a - b #str(a)+" - "+str(b)+" == "+str(an)
                if abs(answers - float(an))<0.001:
                    print("CORRECT")
                    right+=1
                else:
                    print("INCORRECT")
                    wrong+=1
                continue

        '''

        for j,eq,cons,guess in answers:
            eqspl = eq.split(" = ")
            consts = [x for x in eq.split(" ") if x not in ['(',')','+','-','/','*','=','x']]
            #order = int(consts==[x[0] for x in numlist])
            order = int(consts==[x[0] for x in numlist if x[0] in consts])

            if order == 0: continue
            #j = randint(0,len(answers)-1)
            #eq = answers[j]
            trips = []
            #print(j,eq)
            l,r = [x.strip().split(' ') for x in eq.split('=')]
            consts = " ".join([x for x in answers[0][1].split(" ") if x not in ['(',')','+','-','/','*',]])
            consts = consts.split(" = ")
            sp = (objs[consts[0].split(" ")[-1]],objs[consts[1].split(" ")[0]])
             
            target = 'x'
            target = (target,objs[target])

            #find innermost parens?
            sides = []
            thisscore = []
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
                    p,op,e = subeq
                    p = objs[p]
                    e = objs[e]
                    op = op.strip()
                    pute = compute(p,op,e,target,problem,story,order)
                    objs[substr]=pute
                    if pute == -1:
                        exit()
                    score,c,vals = pute
                    thisscore.append(score)
                sides.append(objs[compound[0]])
            p = sides[0]; e = sides[1]
            score = 1
            for s in thisscore: score *= s
            score *= compute(p,'=',e,target,problem,story,order,score,cons)[0]
            scores.append((score,j,eq,guess))
        scores = sorted(scores,reverse=True)
        righties = [x for x in scores[:3] if x[1]==1]
        if not righties:
            wrong+=1
            print(scores[:3])
            print("TOP SCORING NO CORRECT SOLUTION \nINCORRECT")
            continue
        else:
            print(scores[:3])
            corr = righties[0][3]


        '''
        guessd = {}
        for x in scores[:3]:
            if x[3] not in guessd:
                guessd[x[3]]=x[0]
            else:
                guessd[x[3]]+=x[0]

        guessd = sorted(guessd.items(),key=lambda x: x[1],reverse=True)

        if guessd[0][0]==corr:
            right+=1
            print("CORRECT")
        else:
            wrong += 1
            print("INCORRECT")

        '''
        if len(scores)>0:
            if scores[0][1]==1:
                right += 1
                print("CORRECT")
            else:
                wrong += 1
                print("INCORRECT")
        else:
            wrong += 1
            print("INCORRECT")

    return (right,wrong)


def compute(p,op,e,target,problem,story,order,score=None,cons=None):
    if op == '=':
        vec = [order,score,cons]
        vec.extend(makesets.vector(p,e,problem,story,target))
        op_label, op_acc, op_val = svm_predict([-1], [vec], glob ,'-q -b 1')
    else:
        vec = makesets.vector(p,e,problem,story,target)
        op_label, op_acc, op_val = svm_predict([-1], [vec], multi ,'-q -b 1')

    op_val=op_val[0]
    if op == '+':
        val = op_val[0]
    if op == '-':
        val = op_val[1]
    if op == '*':
        val = op_val[2]
    if op == '/':
        val = op_val[3]
    if op == '=':
        val = op_val[0]


    c = makesets.combine(p[1],e[1],op)
    return (val,c,op_val)


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



eq1 = 'DS1/'
eq2 = 'DS2/'
eq3 = 'DS3/'

if __name__=="__main__":
    #q, a = sys.argv[1:3]
    #eqsdir = sys.argv[2]
    #makesets.FOLD = sys.argv[1][-1]
    q,a,e = parse_inp(eq3+'formatted.txt')
    #q2,a2,e2 = parse_inp(eq2+'formatted.txt')
    multi = svm_load_model('data/ixl.local.m')
    glob = svm_load_model('data/ixl.global.m')
    javad_train_local.LEN = len(q)
    LEN = len(q)
    #q = q + q2
    #a = a + a2
    e = [i for i in range(len(q))]#+[LEN+i for i in range(len(q2))]

    right, wrong = make_eq(q,a,e)
    print(right,wrong,right/len(q))

