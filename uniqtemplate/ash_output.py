import signal
import sys
import json
import jsonrpclib
import makesets
import pickle
sys.path.insert(0, '../treebuilder')
from Solver import Solver
from sympy.solvers.solvers import solve
from random import randint
import EntityFileCreator as EF

OUT=None

class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()
def problem_lex(story):
    words = []
    for s in story['sentences']:
        pass 
    #words.extend([x[1]["Lemma"] for x in 

def make_eq(q,a,VERBOSE,TRAIN):
    wps = q

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
 
        story = nlp.parse(problem)
        sets = makesets.makesets(story['sentences'])
        EF.main(sets,k,a[k])
        sets = [x for x in sets if makesets.floatcheck(x[1].num) or x[1].num == 'x']
        print(sets)

        ents = [x[1].entity for x in sets]

        for z in sets:
            z[1].details()

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

    make_eq(q,a,VERBOSE,TRAIN)


