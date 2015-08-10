import sys
import json
import jsonrpclib
#from nltk.corpus import wordnet as wn
#from nltk.corpus import wordnet_ic
import pickle
import numpy as np
#sys.path.insert(0, '/Users/rikka/liblinear-1.94/python')
#from liblinearutil import *
sys.path.insert(0, '/Users/rikka/libsvm-3.18/python')
sys.path.insert(0, '../treebuilder')
from StringTemplate import StringTemplate
from svmutil import *
import makesets
from sympy.solvers.solvers import solve
import vectorize_eqn
import local_score

multi = None
globalm = None

class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()


def compute(p,op,e,target,problem):
    vec = makesets.vector((0,p),(0,e),problem,target)
    #if p.ent == e.ent and op in ['*','/']:
    #    val = 0
    #else:
    if True:
        op_label, op_acc, op_val = svm_predict([-1], [vec], multi ,'-q -b 1')
        #pmop_label, pmop_acc, pmop_val = svm_predict([-1], [vec], pm ,'-q -b 1')
        #mmop_label, mmop_acc, mmop_val = svm_predict([-1], [vec], md ,'-q -b 1')
        op_val=op_val[0]
        #pmop_val = pmop_val[0]
        #mmop_val = mmop_val[0]
        if op == '+':
            val = op_val[0]#*pmop_val[0]
        if op == '-':
            val = op_val[1]#*pmop_val[1]
        if op == '*':
            val = op_val[2]#*mmop_val[0]
        if op == '/':
            val = op_val[3]#*mmop_val[1]


    c = makesets.combine(p,e,op)
    return (val,c)

def cleannum(n):
    return ''.join([x for x in n if x.isdigit() or x=='.' or x=='x' or x=='x*'])


def infer(q,a,VERBOSE):
    wps = q #open(q).readlines()
    answs = a #open(a).readlines()
    problematic = open('somethingWrongProblems','a')

    ar = [0,0]
    sr = [0,0]
    mr = [0,0]
    dr = [0,0]

    replacements = {' two ':' 2 '," three ":' 3 ',' four ':' 4 ',' five ':' 5 ',' six ':' 6 ',' seven ':' 7 ',' eight ':' 8 ',' nine ':' 9 ',' ten ':' 10 ',' eleven ':' 11 ', ' twice ':' 2 '}
    right = 0
    guesses = 0
    ad = []
    wrong = []
    multiops = 0
    multiopsright = 0
    
    replacements = {' two ':' 2 '," three ":' 3 ',' four ':' 4 ',' five ':' 5 ',' six ':' 6 ',' seven ':' 7 ',' eight ':' 8 ',' nine ':' 9 ',' ten ':' 10 ',' eleven ':' 11 ', ' twice ':' 2 '}

    for k in range(len(wps)):
        if VERBOSE:
            for i in range(len(wps)):
                print(i,wps[i])
            k = int(input())
        print(k)
        problem = wps[k].lower()
        
           
        ret = local_score.score(problem)
        if ret == -1:
            wrong.append(k)
            continue

        equations, scores, equalsmatch, contmatch, integerproblem, failurerate, fivescores = ret
        m = np.argmax(scores)
        #print(scores[m],ST.equations[m].toString())
        srt = sorted([(x,i) for i,x in enumerate(scores)],reverse=True)
        print('\n Top scoring 3 equations: ')
        for x,i in srt[:3]:
            print(x,equations[i].toString())


        eqidxs = [y[0] for y in sorted(enumerate(scores),key=lambda x:x[1],reverse=True)]
        eqnidsx = [x[1] for x in srt]
        seen = []
        tright = 0
        globallyadjusted = []
        locally = []
        answ = float(answs[k])
        for i in eqidxs:
            eq = equations[i].toString()
            ogeq = equations[i].toString()
            #eq = eq.replace("=",'-')
            splitEquation = eq.split('=')
            eq = splitEquation[0] + '- (' + splitEquation[1] + ')'
            #print(scores[i], eq)
            try:
                guess = solve(eq,'x')[0]
            except: continue 

            # This is the non-negative constraint
            # wrapped in a "check for complex number" try statement :/
            try:
                if guess < 0:
                    continue
            except:
                continue

            if not guess.is_integer:
                try:
                    int(guess)
                except:
                    if integerproblem:
                        print("Integer problem")
                        continue


            ops = [x for x in equations[i].toString() if x in ['+','-','*','/']]
            
            vec = []
            if equalsmatch[i]=='x':
                equalsmatch[i]= 0 #continue
                contmatch[i]=0
                failurerate[i]=1

            #build training vector

            vec = vectorize_eqn.vec(scores[i],guess,ogeq.strip().split(" "),integerproblem,equalsmatch[i],contmatch[i],problem,failurerate[i],fivescores[i])
            #print(vec)


            op_label, op_acc, op_val = svm_predict([-1], [vec], globalm,'-q -b 1')
            op_val = op_val[0][0]

            locally.append((scores[i],i,guess))
            globallyadjusted.append((op_val,i,guess))
            #globallyadjusted.append(((0.5*op_val)+scores[i],i,guess))
        
        srt = sorted(globallyadjusted,reverse=True)
        print("top 3 globally adjusted:")
        for s,i,guess in srt[:3]:
            print("score : ",s)
            print("eq : ",equations[i].toString())
            print("guess : ",guess)

        srt2 = sorted(locally,reverse=True)
        if srt2[0][0] >0.9:
            srt = srt2
        if len(srt)==0:
            guess = -1
            score = 0
            i = 0
        else:
            if len(srt)==0:
                score,i,guess = (-1,0,-1)
            score,i, guess = srt[0]
        if guess == answ or guess/100 == answ or answ/100 == guess:
            print("\nCORRECT")
            tright=1
        else:

            print("\nINCORRECT")
        print("Guessed Equation : ",equations[i].toString() )

        print("Guess : ",guess,"\nTrue Answer :", answ, '\n\n')
        guesses += 1
        if tright==1:
            if multi:
                multiopsright += 1
            right +=1
        else:
            wrong.append(k)

        #break
        if VERBOSE: input()
        continue
    print(right,guesses)
    #print(multiops,multiopsright)


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



if __name__=="__main__":
    inp, mfile, gfile = sys.argv[1:4]
    q,a,e = parse_inp(inp)
    local_score.multi = svm_load_model(mfile)
    globalm = svm_load_model(gfile)
    VERBOSE=False
    TRAIN=False
    if len(sys.argv)>4:
        if sys.argv[4]=='v':
            VERBOSE=True
    infer(q,a,VERBOSE)


