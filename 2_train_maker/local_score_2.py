import sys
import json
import jsonrpclib
sys.path.insert(0, '../treebuilder')
from StringTemplate import StringTemplate
sys.path.insert(0, '/Users/rikka/libsvm-3.18/python')
from svmutil import *
import makesets
from sympy.solvers.solvers import solve

replacements = {' two ':' 2 '," three ":' 3 ',' four ':' 4 ',' five ':' 5 ',' six ':' 6 ',' seven ':' 7 ',' eight ':' 8 ',' nine ':' 9 ',' ten ':' 10 ',' eleven ':' 11 ', ' twice ':' 2 '}


class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()
VERBOSE = False
multi = None

def setup(m,v):
    global multi, VERBOSE
    multi = m
    VERBOSE = v

def compute(p,op,e,target,problem,story):
    vec = makesets.vector((0,p),(0,e),problem,story,target)
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




def score(problem):

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

    story = nlp.parse(problem)
    sets = makesets.makesets(story['sentences'])

    xidx = [i for i,x in enumerate(sets) if x[1].num=='x']
    twoToRight = False
    if not xidx:
        print("AAAH~! NO X!"); 

    else:

        xidx = xidx[0]
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
    print("Sets detected: ")
    for x in sets:
        x[1].details()
    numlist = [(cleannum(v.num),v) for k,v in sets]
    numlist = [x for x in numlist if x[0]!='']
    if VERBOSE:
        for z,v in numlist:
            v.details()
        input()

    allnumbs = {str(k):v for k,v in numlist}
        

    objs = {k:(0,v) for k,v in numlist}


    constraints = []
    for i in range(len(numlist)):
        if numlist[i][0][-1] == "*":
            if i==0:continue
            constraints.append(numlist[i-1][0]+" * "+numlist[i][0][:-1])
            numlist[i] = (''.join([x for x in numlist[i][0] if x not in ['*','/']]),numlist[i][1])
            numlist[i][1].num = numlist[i][0]
        elif numlist[i][0][0] == "*":
            if i==0:continue
            numlist[i] = (''.join([x for x in numlist[i][0] if x not in ['*','/']]),numlist[i][1])
            tmp = numlist[i-1]
            numlist[i-1]=numlist[i]
            numlist[i]=tmp
            constraints.append(numlist[i-1][0]+" * "+numlist[i][0][1:])
        elif numlist[i][0][-1] == "/":
            if i==0:continue
            constraints.append(" / "+numlist[i][0][:-1])
            numlist[i] = (''.join([x for x in numlist[i][0] if x not in ['*','/']]),numlist[i][1])
    objs = {k:(0,v) for k,v in numlist}
    if 'x' not in objs:
        return -1
    if len(objs)<2:
        return -1
    


    integerproblem = all([float(x[0]).is_integer() for x in numlist if x[0]!='x'])

    numidxlist = [x[0] for x in numlist]
    ST = StringTemplate(numidxlist, inf=True)
    scores = []
    equalsmatch = []
    contmatch = []
    failurerate = []
    for j,eq in enumerate(ST.equations):
        #print(j,eq.toString())
        good = False
        '''
        if len(constraints)==0:
            good = True
        else:
            for constraint in constraints:
                if constraint in eq.toString():
                    good = True
        if not good:
            scores.append(-0.2)
            continue
        '''
        
                
        thisscore = []
        #print(eq.toString())
        #determine score for this eq
        l,r = [x.strip().split(' ') for x in eq.toString().split('=')]
        #print(l,r)
        
        if twoToRight:
            if len(r)!=3 and len(l)!=3:
                scores.append(-0.2);
                equalsmatch.append('x');
                contmatch.append('x')
                failurerate.append('x')
                continue
            if len(r)==3: 
                compound = r
                target = 'x'
            else:
                compound = l
                target = 'x'

        else:
            if len(r)>1 and len(l)>1:
                scores.append(-0.2);
                equalsmatch.append('x');
                contmatch.append('x')
                failurerate.append('x')
                continue
            if len(r)>1: 
                compound = r
                target = l[0]
            else:
                compound = l
                target = r[0]

        target = (target,objs[target])

        #find innermost parens?
        sides = []
        for i,compound in enumerate([l,r]):
            c = None
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
                if substr in objs:
                    pute = objs[substr]
                    #print(pute[0],pute[1].num)
                else:
                    p,op,e = subeq
                    #print(p,op,e)
                    p = objs[p][1]
                    e = objs[e][1]
                    op = op.strip()
                    pute = compute(p,op,e,target,problem,story)
                    #print("OPERATION SELECTED: ",op)
                    #p.details()
                    #e.details()
                    #print(substr,pute[1].num)
                    objs[substr]=pute
                if pute == -1:
                    exit()
                score,c = pute
                thisscore.append(score)
            if c == None:
                score,c = objs[compound[0]]
                thisscore.append(score)
            sides[i]=c
        thisscore.append(score)
        if sides[0].entity == sides[1].entity:
            #thisscore.append(-0.2)
            equalsmatch.append(1)
        else:
            equalsmatch.append(0)

        failurerate.append(sum([objs[x][1].type_failure for x in objs]))


        if target[1][1].container != c.container:
            contmatch.append(1)
        else: contmatch.append(0)

        if len(thisscore)==0:
            scores.append(0)
        else:
            scores.append(sum(thisscore)/float(len(thisscore)))



    return (ST.equations, scores, equalsmatch, contmatch, integerproblem,failurerate)
        
