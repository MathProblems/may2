import signal
import sys
import json
import jsonrpclib
from markIrrelev import aset
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

def cleannum(n):
    return ''.join([x for x in n if x.isdigit() or x=='.' or x=='x' or x=='x*'])


def make_eq(q,a,VERBOSE,TRAIN):
    bigtexamples = {x:([],[]) for x in ["+","*",'/','-','=']}
    #wps = open(q).readlines()
    #answs = open(a).readlines()
    #VERBOSE=True
    wps = q

    IRR = open("output_relevant.txt").readlines()
    IRR = [x.strip().split(" ") for x in IRR]
    IRR = [[y.split(",")[1:] for y in x] for x in IRR]

    wps = pickle.load(open('irrelevSets.pickle','rb'))
    

    


    for k, sets in wps:
        print(k)
        EF.main(sets,k,a[k])
        sets = [x for x in sets if makesets.floatcheck(x[1].num) or x[1].num == 'x']
        print(sets)
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
    '''
    if len(sys.argv)>3:
        if sys.argv[3]=='v':
            VERBOSE=True
        elif sys.argv[3]=='t':
            TRAIN = True
            OUT = sys.argv[4]
    '''
    make_eq(q,a,VERBOSE,TRAIN)


