import sys
import json
import jsonrpclib
import makesets
import pickle
sys.path.insert(0, '../treebuilder')
from Solver import Solver
from sympy.solvers.solvers import solve
from random import randint

OUT=None

class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()

def cleannum(n):
    return ''.join([x for x in n if x.isdigit() or x=='.' or x=='x' or x=='x*'])

def kill(signum, frame):
    raise Exception("end of time")

def training(trips,problem,target):
    #this function take the trips and creates positive and negative training instances from them
    
    texamples = {x:([],[]) for x in ["+","*",'/','-','=']}
    for op,a,b in trips:
        vec = makesets.vector(a,b,problem,target)
        texamples[op][0].append(vec)

    return texamples


def make_eq(q,a,VERBOSE,TRAIN):
    bigtexamples = {x:([],[]) for x in ["+","*",'/','-','=']}
    wps = open(q).readlines()
    answs = open(a).readlines()
    if not TRAIN and not VERBOSE:
        out = open(q+".out.txt",'w')
    problematic = open('somethingWrongProblems','w')


    

    replacements = {' two ':' 2 '," three ":' 3 ',' four ':' 4 ',' five ':' 5 ',' six ':' 6 ',' seven ':' 7 ',' eight ':' 8 ',' nine ':' 9 ',' ten ':' 10 ',' eleven ':' 11 ', ' twice ':' 2 '}

    for k in range(len(wps)):
        if VERBOSE:
            for i in range(len(wps)):
                print(i,wps[i])
            k = int(input())
        print(k)
        problem = wps[k].lower()
        #First preprocessing, tokenize slightly
        problem = problem.strip().split(" ")
        for i,x in enumerate(problem):
            if len(x)==0:continue
            if x[-1] in [',','.','?']:
                problem[i] = x[:-1]+" "+x[-1]
        problem = ' '.join(problem)
        problem = " " + problem + " "
        print(problem)

        for r in replacements:
            problem = problem.replace(r,replacements[r])
        
        '''
        if " how " in problem:
            left,right = problem.split(" how ")
        else: left = problem

        for r in replacements:
            left = left.replace(r,replacements[r])
        if " how " in problem:
            problem = left + ' how ' + right
        else:
            problem = left
        '''

        story = nlp.parse(problem)
        sets = makesets.makesets(story['sentences'])
        i = 0
        print(sets)
        while i < len(sets):
            dups = [y for y in sets if y[1].idx != None]
            dups = [y for y in dups if y[1].idx == sets[i][1].idx]
            if len(dups)>1:
                good = [y for y in dups if len([x for x in y[1].num if x.isdigit()])>0]
                if good:
                    others = [x for x in dups if x!=good[0]]
                    for x in others:
                        sets.remove(x)
                else:
                    # just pick 1
                    for x in dups[1:]:
                        sets.remove(x)
            i+=1


        xidx = [i for i,x in enumerate(sets) if x[1].num=='x']
        if not xidx:
            problematic.write('no x :'+problem); continue

        #TODO look for 2 xes
        xidx = xidx[0]
        twoToRight = False
        if xidx>0:
            print(len(sets),xidx)
            if sets[xidx-1][1].entity == 'dozen': 
                # 2 vals to right
                twoToRight = True
        if len(sets)-xidx>1:    
            if sets[xidx+1][1].entity == 'dozen':
                twoToRight=True
        if len(sets)-xidx<3:
            if sets[xidx][1].entity=='dozen':
                twoToRight=True


        



        numlist = [(cleannum(v.num),v) for k,v in sets]
        numlist = [x for x in numlist if x[0]!='']
        if VERBOSE:
            for z,v in numlist:
                v.details()
            input()

        allnumbs = {str(k):v for k,v in numlist}
            

        objs = {k:(0,v) for k,v in numlist}

        print('start solving')
        print(numlist)
        if len(numlist)<2:
            problematic.write("not enough numbers : "+problem);continue
            
        values = [x[0] for x in numlist if x[0]!='x']
        print(values)
        ST = Solver(values)

        answers = []
        answers = ST.solveEquations(float(answs[k]))
        print(answs[k])
        if not answers:
            problematic.write("No answers : " + problem + "\n")
            problematic.write(str([x[0] for x in numlist])+'\n')
            problematic.write(answs[k]+'\n')
            continue
        print('done solving')

        # if target has 2 entities, try eqs with = x op y format
        simpleranswers = None
        if twoToRight:
            try:
                simpleranswers = [x for x in answers if x.split(" ")[-4]=="=" and (x.split(" ")[-3]=='x' or x.split(' ')[-1]=='x')]
            except:
                pass
        if not simpleranswers:
            simpleranswers = [x for x in answers if x.split(" ")[1] == '=' or x.split(" ")[-2]=="="]
        #simpleranswers = [x for x in answers if x.split(" ")[1] == '=' or x.split(" ")[-2]=="="]

        #filter out where = in middle if simpler eq exists
        if simpleranswers:
            print(answers)
            answers = simpleranswers[:]
        else:
            problematic.write("not simple : "+problem+"\n");continue

        values = [x[0] for x in numlist]
        xidx = values.index('x')
        print(simpleranswers)
        print(xidx)
        for a in simpleranswers:
            aspl = [x for x in a.split(" ") if x not in ["/","-",'+','*','=','(',')']]
            print(a);print(aspl);print(values)
            aidx = aspl.index('x')
            print(aidx)
            if aidx != xidx:
                print("removing ",a)
                answers.remove(a)
        print(answers)
        if answers==[]:
            answers = simpleranswers


        
        print(answers)
        if not VERBOSE:
            if not TRAIN:
                out.write(problem + '\n')
                out.write(answs[k] + "\n")
                out.write(str([x[0] for x in numlist]))
                out.write("\n")
                for x in answers:
                    out.write(x + "\n")
                out.write("___\n")

        if VERBOSE:
            input()
        if not TRAIN:
            continue

        if len([x for x in answers if x.split(" ")[-2]=="="])>0:
            answers = [x for x in answers if x.split(" ")[-2]=="="]

        c = randint(0,len(answers)-1)
        answers = [answers[c]]
        for j,eq in enumerate(answers):
            trips = []
            print(j,eq)
            l,r = [x.strip().split(' ') for x in eq.split('=')]
            
            compound = r if len(l)==1 else l
            simplex = l if len(l)==1 else r
            target = simplex[0]
            target = (target,objs[target])

            #find innermost parens?
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
                    #print(p,op,e)
                    p = objs[p]
                    e = objs[e]
                    op = op.strip()
                    trips.append((op,p,e))
                    pute = (0,makesets.combine(p[1],e[1],op))
                    #print("OPERATION SELECTED: ",op)
                    #p.details()
                    #e.details()
                    #print(substr,pute[1].num)
                    objs[substr]=pute
                if pute == -1:
                    exit()
            if simplex == l:
                trips.append(("=",objs[simplex[0]],objs[compound[0]]))
            else:
                trips.append(("=",objs[compound[0]],objs[simplex[0]]))
            t = training(trips,problem,target)
            for op in t:
                bigtexamples[op][0].extend(t[op][0])
                bigtexamples[op][1].extend(t[op][1])
            print(op,len(bigtexamples[op][0]))
    if TRAIN:
        pickle.dump(bigtexamples,open('data/'+OUT+".training",'wb'))



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
    #q, a = sys.argv[1:3]
    inp = sys.argv[1]
    q,a,e = parse_inp(inp)

    VERBOSE=False
    TRAIN=False
    if len(sys.argv)>3:
        if sys.argv[3]=='v':
            VERBOSE=True
        elif sys.argv[3]=='t':
            TRAIN = True
            OUT = sys.argv[4]
    make_eq(q,a,VERBOSE,TRAIN)


