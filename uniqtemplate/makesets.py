import sys
import json
import jsonrpclib
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic
import pickle
brown_ic = wordnet_ic.ic('ic-brown.dat')
import unitConversion as uc


class aset:

    def __init__(self,num=None,entity=None,surface=None,idx=None):
        self.num = num
        self.entity = entity
        self.surface = surface
        self.idx = idx
        self.widx = (idx%1000)+1 if idx is not None else None
        self.container = None
        self.verbs = None
        self.adjs = None
        self.location = None
        self.contains = None
        self.compound = 0
        self.subtypes = []
        self.type_failure = 0

    def details(self,sf=True):

        string = "_____________\n"
        ordrd = sorted(self.__dict__.items())
        for x,y in ordrd:
            string += str(x)+" : "+str(y)+"\n"
        string += "_____________\n"
        if sf:
            print(string)
        else:
            return string


def vector(a,b,problem,story,target,feats=False):
    a = a[1]
    b = b[1]

    vec = []
    features = []
    features.append("a compound?")
    vec.append(int(a.compound))

    features.append("b compound?")
    vec.append(int(b.compound))

    features.append("a subtype of b")
    vec.append(int(a.entity in b.subtypes))

    features.append("b subtype of a")
    vec.append(int(b.entity in a.subtypes))

    features.append("a contians b entity match")
    if a.contains == None and b.entity == None: vec.append(0)
    elif a.contains == None or b.entity == None: vec.append(-1)
    elif b.entity in a.contains: vec.append(1)
    else: vec.append(-1)

    features.append("b contains a entity match")
    if b.contains == None and a.entity == None: vec.append(0)
    elif b.contains == None or a.entity == None: vec.append(-1)
    elif a.entity in b.contains: vec.append(1)
    else: vec.append(-1)


    features.append("acontainer bentity match")
    if a.container == None and b.entity == None: vec.append(0)
    elif a.container == None or b.entity == None: vec.append(-1)
    elif b.entity in a.container: vec.append(1)
    else: vec.append(-1)

    features.append("bcontainer aentity match")
    if b.container == None and a.entity == None: vec.append(0)
    elif b.container == None or a.entity == None: vec.append(-1)
    elif a.entity in b.container: vec.append(1)
    else: vec.append(-1)

    features.append("b container a entity match")
    if b.container == None and a.container == None: vec.append(0)
    elif b.container == None or a.container==None: vec.append(-1)
    else:
        bcont = b.container.split(" ")[-1]
        acont = a.container.split(" ")[-1]
        if bcont==acont: vec.append(1)
        else: vec.append(-1)

    features.append("entity match")
    if b.entity == None and a.entity == None: vec.append(0)
    elif b.entity == a.entity: vec.append(1)
    else: vec.append(-1)

    features.append("adj match")
    if b.adjs == None and a.adjs == None: vec.append(0)
    elif b.adjs == a.adjs: vec.append(1)
    else: vec.append(-1)

    features.append("loc match")
    if b.location == None and a.location == None: vec.append(0)
    elif b.location == a.location: vec.append(1)
    else: vec.append(-1)

    features.append('number distances')
    try:
        distance = int(a.idx)-int(b.idx)
        distance = 1 / ( 10000 - distance )
    except: distance = 1
    vec.append(distance)

    asidx = a.idx//1000
    bsent = b.idx//1000




    features.append('a is target')
    if a.num == 'x': vec.append(1)
    else: vec.append(0)
    features.append('b is target')
    if b.num == 'x': vec.append(1)
    else: vec.append(0)

    features.append('a target match')
    if a.entity==target: vec.append(1)
    else: vec.append(0)
    features.append('b target match')
    if b.entity==target: vec.append(1)
    else: vec.append(0)


    asidx = a.idx//1000
    bsidx = b.idx//1000
    story = story['sentences']
    asent = [x[0] for x in story[asidx]['words']]
    bsent = [x[0] for x in story[bsidx]['words']]
    #words inbetween features
    awidx = a.idx%1000
    bwidx = b.idx%1000
    allwords = []
    for j in range(len(story)):
        for i,x in enumerate(story[j]['words']):
            allwords.append((j*1000+i,x[0]))
    wordseg = [x[1] for x in allwords if x[0]>a.idx and b.idx>x[0]]
    for item in [',','and','but']:
        features.append(item)
        if item in wordseg:
            vec.append(1)
        else:
            vec.append(0)

    features.extend(["a times",'b times',"a total",'b total',"a together",'b together',"a more", 'b more' ,"a less",'b less',"a add",'b add',"a divide",'b divide',"a split",'b split',"a equal",'b equal',"a equally",'b equally'])
    for li in ["times","total","together","more","less","add","divide","split","equal","equally"]:
        if li in asent:
            vec.append(1)
        else:
            vec.append(0)
        if li in bsent: vec.append(1)
        else: vec.append(0)

    #target features
    problem = story[-1]['text']
    if " how " in problem:
        problem = problem.split(" how ")[-1]
    elif " what " in problem:
        problem = problem.split(" what ")[-1]

    if " , " in problem:
        problem = problem.split(" , ")[0]
    features.append("in all")
    if "in all" in problem: vec.append(1)
    else: vec.append(0)
    features.append("end with")
    if "end with" in problem: vec.append(1)
    else: vec.append(0)
    problem = problem.split()
    features.extend(["times","total","together","more","less","add","divide","split","left","equal","equally","now",'left','start'])
    for li in ["times","total","together","more","less","add","divide","split","left","equal","equally","now",'left','start']:
        if li in problem:
            vec.append(1)
        else:
            vec.append(0)


    if a.verbs == None or b.verbs == None:
        dist = 1
    else:
        avl = a.verbs.split(" ")
        bvl = b.verbs.split(" ")

        if len([x for x in avl if x in bvl ])>0:
            dist = 0
        else:
            dist = 1
            for aw in avl:
                asyns = wn.synsets(aw)
                for asyn in asyns:
                    for bw in bvl:
                        bsyns = wn.synsets(bw)
                        for bsyn in bsyns:
                            if asyn._pos == bsyn._pos: 
                                try:
                                    sim = 1/(1+bsyn.res_similarity(asyn,brown_ic))
                                except:
                                    sim = 2
                                if sim < dist:
                                    dist = sim
    features.append("Verb distance")
    vec.append(dist)

    #verb similarity
    verbs = ['be', 'do', 'go', 'have', 'leave', 'keep', 'get', 'make', 'tell', 'place', 'lose', 'change', 'give', 'hand', 'take', 'buy', 'receive', 'put', 'set', 'like', 'want', 'call', 'divide', 'split']

    for v in verbs:
        features.append(v)
        vsyns = wn.synsets(v, pos='v')

        dist = 1
        if b.verbs is not None:
            for verb in b.verbs.split(' '):
                bsyns = wn.synsets(verb, pos='v')
                if verb == v:
                    dist = 0
                else:
                    for vsyn in vsyns:
                        for bsyn in bsyns:
                            try:
                                sim = 1/(1+vsyn.lin_similarity(bsyn,brown_ic))
                            except:
                                sim = 2
                            if sim < dist:
                                dist = sim
        vec.append(dist)
    if feats:
        return (features, vec)
    else:
        return vec



def combine(a,b,op):
    #takes two entities and returns a combo of them.
    c = aset()
    if a.container == b.entity or op == '-':
        #multiplication or subtraction swap
        t = a
        a = b
        b = t



    for k in a.__dict__:
        if k == "num":
            c.num = "("+str(a.__dict__[k])+op+str(b.__dict__[k])+")"
        elif k in ['container','contains']:
            c.__dict__[k]=None
        else:
            c.__dict__[k]= b.__dict__[k]
    #print(c.__dict__)
    if op == '*':
        if a.entity == b.entity:
            c.type_failure = 1
    c.compound = 1
    c.subtypes = [a.entity,b.entity]
    return c



def entityextract(story):
    sets = []
    #this function makes the preliminary sets, finding the quantified entities. 
    for j,s in enumerate(story):
        deps = s['indexeddependencies']
        words = s['words']
        surfaces = [x[0] for x in words]
        
        nums = [(x[1],x[2]) for x in deps if x[0]=='num' or x[0]=='number' or x[0]=='det']
        nums.extend([(x[2],x[1]) for x in deps if x[0]=="prep_of" and (x[1].split("-")[0].isdigit() or x[1].rsplit("-",maxsplit=1)[0] in ['half','third','quarter'])])
        for w,n in nums:
            n,nidx = n.split("-")
            nidx = int(nidx)-1
            w,widx = w.rsplit("-",maxsplit=1)
            widx = int(widx)-1
            #print(w,n)
            if w == "$":
                lemma = 'dollar'
                sets.append(((j*1000)+nidx,aset(n,lemma,w,j*1000+widx)))



            elif words[widx][1]["PartOfSpeech"] in ["NN","NNS"]:
                if n=='each' and w=='cost':
                    #let this slip through
                    continue
                lemma = words[widx][1]["Lemma"]
                sets.append(((j*1000)+nidx,aset(n,lemma,w,j*1000+widx)))
    
        #deal with each where parse fails AND IS BAD:
        if 'each' in surfaces:
            eachi = surfaces.index('each')
            if (j*1000)+eachi in [x[0] for x in sets]:
                continue
            setmatch = [x for x in words[eachi:eachi+4] if x[1]['Lemma'] in [y[1].entity for y in sets]]
            if setmatch and len([x for x in words[eachi:eachi+4] if x[0] in [',','and','but']])==0:
                nextword = setmatch[0]
            else:
                setmatch = [x for x in words if x[1]['Lemma'] in [y[1].entity for y in sets]]
                if setmatch:
                    nextword = setmatch[0]
                else:
                    nns = [x for x in words if x[1]["PartOfSpeech"]=="NNS"]
                    if nns:
                        nextword = nns[-1]
            lemma = nextword[1]["Lemma"]
            sets.append(((j*1000)+eachi,aset('each',lemma,nextword[0],j*1000+eachi+1)))

    #get question entity
    ents = [x[1].entity for x in sets]
    q = story[-1]
    j = len(story)-1
    words = q["words"]
    deps = q['indexeddependencies']
    good = 0
    if "what" in [x[0] for x in words]:
        targets = [x[2] for x in deps if 'what' in x[1] and x[0]=='nsubj']
        if len(targets)==1:
            t,tidx = targets[0].rsplit("-",maxsplit=1)
            tidx = int(tidx)-1
            lemma = words[tidx][1]["Lemma"]
            sets.append((j*1000+tidx,aset('x',lemma,t,j*1000+tidx)))
    if "how" in [x[0] for x in words]:
        targets = [x[1] for x in deps if x[2].rsplit("-",maxsplit=1)[0] in ['many','much']]
        wzeros = [x[0] for x in words]
        if 'much' in wzeros:
            if 'cost' in wzeros or 'spend':
                tidx = len(words)-1
                sets.append((j*1000+tidx,aset('x','dollar',"dollar",j*1000+tidx)))
                good = 1
                targets = []


        if len(targets)==1:
            t,tidx = targets[0].rsplit("-",maxsplit=1)
            tidx = int(tidx)-1
            if words[tidx][1]["PartOfSpeech"] in ["NN","NNS"]:
                lemma = words[tidx][1]["Lemma"]
                #check for dozen
                if len([x for x in deps if targets[0]==x[1] and x[0]=='nn' and 'dozen' in x[2]])>0:
                    sets.append((j*1000+tidx-1,aset('x','dozen','dozen',j*1000+tidx)))
                    sets.append((j*1000+tidx,aset('dozen',lemma,t,j*1000+tidx)))
                else:
                    sets.append((j*1000+tidx,aset('x',lemma,t,j*1000+tidx)))
                good = 1
            else:
                good = 0
                if t == "more":
                    targets = [x[1] for x in deps if x[2].rsplit("-",maxsplit=1)[0] in ['more']]
                    if targets:
                        t,tidx = targets[0].rsplit("-",maxsplit=1)
                        tidx = int(tidx)-1
                        if words[tidx][1]["PartOfSpeech"] in ["NN","NNS"]:
                            lemma = words[tidx][1]["Lemma"]
                            sets.append((j*1000+tidx,aset('x',lemma,t,j*1000+tidx)))
                            good = 1
                elif t == 'did':
                    targets = [x[2] for x in deps if x[1].rsplit("-",maxsplit=1)[0] in ['did'] and x[0]=='nsubj']
                    if targets:
                        t,tidx = targets[0].rsplit("-",maxsplit=1)
                        tidx = int(tidx)-1
                        if words[tidx][1]["PartOfSpeech"] in ["NN","NNS"]:
                            lemma = words[tidx][1]["Lemma"]
                            sets.append((j*1000+tidx,aset('x',lemma,t,j*1000+tidx)))
                            good = 1
    
                if good == 0:
                    sets.append((j*1000+tidx,aset('x','NONE','NONE',None)))
                    good = 1
        else:
            howidx = [i for i,x in enumerate(words) if x[0]=='how'][0]
            nextword = words[howidx+1]
            if nextword[0] == 'far':
                sets.append((j*1000+howidx+1,aset('x','DISTANCE','DISTANCE',None)))
                good = 1
            elif nextword[0] == 'long':
                sets.append((j*1000+howidx+1,aset('x','LENGTH','LENGTH',None)))
                good = 1



            
    for j,s in enumerate(story):
        deps = s['indexeddependencies']
        words = s['words']
        othernums = [((j*1000+i), x[0]) for i,x in enumerate(words) if x[1]["PartOfSpeech"]=="CD"]
        othernums = [x for x in othernums if x[0] not in [y[0] for y in sets]]
        if othernums:
            for idx,n in othernums:
                prev=1
                #this is a hack To fix the "and" bug
                if 'and' in [x[0] for x in words[idx%1000:idx%1000+7]]:
                    #use next jawn
                    nextjawn = [x for x in sets if x[0]>idx and x[0]<(((idx//1000)+1)*1000)]
                    if nextjawn:
                        nextjawn = nextjawn[0][1]
                        sets.append((idx,aset(n,nextjawn.entity,nextjawn.surface,None)))
                        prev=0
                if prev==1:
                    prevjawn = [x for x in sets if x[0]<idx]
                    if prevjawn:
                        #prev quantified jawns:
                        pqjawns = [x for x in prevjawn if floatcheck(x[1].num)]
                        if pqjawns:
                            prevjawn = pqjawns[-1][1]
                        else:
                            prevjawn = prevjawn[-1][1]
                        sets.append((idx,aset(n,prevjawn.entity,prevjawn.surface,None)))
                    else:
                        #find the NNSess
                        #print(idx,n)
                        nns = []
                        for j,s in enumerate(story):
                            nns.extend([(j*1000+i,w) for i,w in enumerate(s['words']) if w[1]["PartOfSpeech"] == "NNS"])
                        #print(nns)
                        if nns:
                            prev = [x[1] for x in nns if x[0]<idx]
                            if prev:
                                prevjawn = prev[-1]
                                sets.append((idx,aset(n,prevjawn[1]["Lemma"],prevjawn[0],None)))
                            else:
                                prevjawn = nns[0][1]
                                sets.append((idx,aset(n,prevjawn[1]["Lemma"],prevjawn[0],None)))


    
    xset = [x for x in sets if x[1].num=='x']
    if xset and good == 0:
        xset = xset[0]
        if xset[1].entity=="NONE":
            #is there a NNS near to the question?
            words = story[-1]['words']
            idx = [x[0] for x in words].index('how')
            prev = 1
            if idx>=0:
                words = words[idx:idx+4]
                nns = [x for x in words if x[1]['PartOfSpeech']=='NNS']
                if nns:
                    xset[1].entity = nns[0][1]["Lemma"]
                    xset[1].surface = nns[0][0]
                    prev = 0

            if prev:
                prev = [x for x in sets if x[0]<xset[0]]
                prev = prev[-1][1]
                xset[1].entity = prev.entity
                xset[1].surface = prev.surface

        quantifiedents = [x[1].entity for x in sets if floatcheck(x[1].num) or x[1].num=='dozen']
        if quantifiedents:
            if xset[1].entity not in quantifiedents:
                
                #change, make most prev entity rather than whatever ent
                #unless its like money or something!?
                if xset[1].entity not in ['dozen','money','$','money','cent','penny', 'nickel', 'dime', 'quarter', 'half-dollar', 'dollar', 'five-dollar bills','second', 'minute', 'hour', 'day', 'week', 'month', 'year','inches', 'feet', 'yards']:
                    xset[1].entity = quantifiedents[-1]

    sets = sorted(sets)
    return sets
    

def distance(a,b,story):
    pass
    

def containers(sets,story):
    for j,s in enumerate(story):
        deps = s['indexeddependencies']
        thissentsets = [x for x in sets if x[0]//1000 == j]

        #deal with dozens
        dozenents = [x for x in thissentsets if x[1].num == 'dozen']
        thisdozen = [x for x in thissentsets if x[1].entity == 'dozen']
        if dozenents:
            for x in dozenents:
                if thisdozen:
                    thisdozen[0][1].contains = x[1].entity
                    if thisdozen[0][1].num != 'x' and not floatcheck(thisdozen[0][1].num):
                        thisdozen[0][1].num = '1'
                else:
                    dozent = aset('1','dozen','dozen',None)
                    dozent.contains = x[1].entity
                    sets.append((x[0]-1,dozent))
                    
                x[1].container = 'dozen'
                x[1].num = '12'
                


        else:
            if thisdozen:
                dozdeps = [x[2].split('-') for x in deps if 'dozen' in x[1] and 'many' not in x[0]]
                if dozdeps:
                    #print(dozdeps)
                    wrds = [s['words'][int(x[1])-1] for x in dozdeps]
                    wrds = [x for x in wrds if x[1]['PartOfSpeech'] in ['NN','NNS']]
                    if wrds:
                        wrd = wrds[0]
                        lem = wrd[1]['Lemma']
                        surf = wrd[0]
                        dozent = aset('12',lem,surf,None)
                        thisdozen[0][1].contains = lem
                        dozent.container = 'dozen'
                        sets.append((thisdozen[0][0]+1,dozent))

        #deal with each
        thiseach = [x for x in thissentsets if x[1].num in ['each','a','an','the','every','per','one','1']]
        if len(thiseach)>0:
            thisothers = [x for x in thissentsets if x not in thiseach]
            if thisothers:
                for eidx,e in thiseach:
                    #which is closer: next ent or prev?
                    if e.num in ['a','an','per']:
                        prev = [x for x in thisothers if x[0]<eidx and x[0]>eidx-5]
                        if prev:
                            target=prev[-1]
                            target[1].container = e.entity
                            e.contains = target[1].entity
                    else:
                        eachdeps = [x[2] for x in deps if e.surface in x[1]]
                        eachdeps += [x[1] for x in deps if e.surface in x[2]]
                        meachdeps = [s['words'][int(x.split('-')[-1])-1][1]['Lemma'] for x in eachdeps]
                        #e.details()
                        #print(eachdeps)
                        eachdeps = [y for y in sets if floatcheck(y[1].num) and y[1].entity in meachdeps and y[1].surface + "-"+str(y[1].widx) in eachdeps]
                        #print(eachdeps,eidx)
                        if eachdeps:
                            try:
                                each0 = sorted([(abs(y[0]-eidx),y[1]) for y in eachdeps],reverse=True)[0]
                            except:
                                each0 = eachdeps[0]
                            each0[1].container = e.entity
                            e.contains = each0[1].entity
                        else:
                            prev = [x for x in thisothers if x[0]<eidx]
                            nexxt = [x for x in thisothers if x[0]>eidx]
                            if not nexxt:
                                target = prev[-1]
                            else:
                                #really should check distances, but for now lets not
                                target = nexxt[0]
                            target[1].container = e.entity
                            e.contains = target[1].entity
                        

        for e in thissentsets:

            #get verbs, adj, location
            esurface = e[1].surface+'-'+str(e[1].widx)
            #print(esurface)
            vbs = [x for x in deps if x[2]==esurface and x[0]=='dobj']
            if vbs:
                e[1].verbs = ' '.join([x[1].split('-')[0] for x in vbs])

            adjs = [x for x in deps if x[1]==esurface and x[0]=='amod']
            if adjs:
                e[1].adjs = ' '.join([x[2].split('-')[0] for x in adjs])

            # location
            elocs = [x[2].split("-")[0] for x in deps if x[0] in ['prep_in','prep_on','prep_at'] and x[1] == esurface]
            if elocs:
                e[1].location = ' '.join(elocs)

            if e[1].container:
                continue


            # container is nsubj
            if vbs:
                for x in vbs:
                    verb = x[1]
                    #find subj, this is container
                    vsubj = [x for x in deps if x[1]==verb and x[0] in ['nsubj','nsubjpass']]
                    if vsubj:
                        e[1].container = ' '.join([x[2].split('-')[0] for x in vsubj])
            if not e[1].verbs:
                vbs = [x[1]["Lemma"] for x in s['words'] if 'VB' in x[1]['PartOfSpeech']]
                vbs2 = [x for x in vbs if x not in ['do','be','have','need']]
                if vbs2:
                    e[1].verbs = ' '.join(vbs2)
                else:
                    e[1].verbs = ' '.join(vbs)

    return sets

def floatcheck(n):
    try:
        n = ''.join([x for x in n if x!=','])
        n = float(n)
        return True
    except:
        return False
    

def fix_each(sets):

    eaches = [x for x in sets if x[1].num in ['each','every','per','a','an','per','one']]
    for x in eaches:
        moveto = [y for y in sets if y[1].entity == x[1].entity and floatcheck(y[1].num)]
        if moveto:
            moveto = moveto[0]
            if x[0] > moveto[0]:
                moveto[1].contains = x[1].contains
                sets.remove(x)
            else:
                x[1].contains = moveto[1].contains
                x[1].num = moveto[1].num
                sets.remove(moveto)
        else:
            x[1].num == '1'

    i=0
    while i<len(sets):
        if sets[i][1].container:
            containers = [x for x in sets if x[1].entity == sets[i][1].container and x[1].contains == sets[i][1].entity and floatcheck(x[1].num)]
            if containers:
                sets[i] = (containers[0][0]+1,sets[i][1])
        i+=1

    '''
    for i in range(len(sets)):
        idx,e = sets[i]
        #if e.num in ['each','a','an','the','every']:
        if e.contains is not None:
            #others = [x for x in sets if x[1].entity == e.entity and x[0] != idx and len([y for y in x[1].num if y.isdigit()])>0]
            #if len(others)>=1:
                if len(sets)>i+1:
                    if sets[i+1][1].entity == e.contains:
                        if sets[i+1][1].num == 'x':
                            #move x to set
                            sets[i+1] = (idx-1,sets[i+1][1])
                        else:
                            idx = sets[i+1][0]+1
                            sets[i] = (idx,e)
                        
                #e.num = '1'
            others = [x for x in sets if x[1].entity == e.entity and x[0] != idx]
            others = [x for x in others if x[1].num=='x' or floatcheck(x[1].num)]
            onum = [x[1].num for x in others]
            if 'x' in onum:
                e.num = 'x'
            elif others:
                prev = [x for x in others if x[0]<idx]
                if prev:
                    prev = prev[-1]
                    idx = sets.index(prev)
                    sets[idx]
                    e.num = prev[-1][1].num
                    prev[-1][1].num = "USED"
                else:
                    e.num = others[0][1].num
                    others[0][1].num="USED"
    '''
                
    return sets

        
def circumscription(sets,story):
    setssofar = []
    for j,s in enumerate(story):
        deps = s['indexeddependencies']
        words = s['words']
        setssofar.extend([x for x in sets if x[0]//1000 == j])
        thissentnums = [(i,x) for i,x in enumerate(words) if x[1]["PartOfSpeech"]=='CD']

def add_bare_sets(sets,story):
    quantifiedents = [x[1].entity for x in sets if floatcheck(x[1].num) or x[1].num in ['dozen','half']]
    #print(quantifiedents)
    
    for j,s in enumerate(story):
        thissentsets = [x for x in sets if x[0]//1000 == j]
        thissentids = [x[1].widx for x in thissentsets]
        for i,w in enumerate(s['words']):
            if i+1 in thissentids:
                continue
            if w[1]['Lemma'] in quantifiedents:
                sets.append(((j*1000)+i,aset('BARE',w[1]['Lemma'],w[0],j*1000+i)))

    return sets

def fix_times(sets):
    times = [x for x in sets if x[1].entity == 'time']
    if times:
        for x in times:
            pcontainer = [y[1].container for y in sets if y[0] < x[0] and y[1].container != None]
            if pcontainer:
                x[1].entity = pcontainer[-1]
    return sets

def move_x(sets,story):
    targets = [(i,x) for i,x in enumerate(sets) if x[1].num == 'x']
    if not targets:
        return sets
    target = targets[0][1][1].entity

    #first process question
    q = story[-1]
    j = len(story)-1
    startwords = ['begin','start']
    endwords = ['leave','remain','finish']
    qlem = [x[1]['Lemma'] for x in q['words']]
    if len([x for x in startwords if x in qlem])>0:
        #move x to beginning
        sets[targets[0][0]] = (0,targets[0][1][1])
        return sets
    if len([x for x in endwords if x in qlem])>0:
        return sets

    spots = []
    for j,s in enumerate(story):
        thissentsets = [x for x in sets if x[0]//1000 == j]
        potentials = [(i,x) for i,x in enumerate(s['words']) if x[1]["Lemma"]==target]
        for i,p in potentials:
            smatch = [x for x in thissentsets if x[1].surface == p[0] and x[1].widx == i+1]
            if smatch:
                smatch = [x for x in smatch if x[1].num != 'x' and not floatcheck(x[1].num)]
                spots.extend([(x[0],x[1].num) for x in smatch])
            else:
                #assure this is the only set ref in the vicinity
                closesets = [x for x in sets if abs(x[0]-(j*1000+i))<10]
                if len(closesets)==0:
                    spots.append((j*1000+i,'BARE'))
                

    if spots:
        bspots = [x for x in spots if x[1]!='BARE']
        if bspots:
            #move to bspots 0 
            place = bspots[0][0]
        else:
            place = spots[0][0]
        #print("moving x")
        #print(targets,spots,place)
        sets[targets[0][0]] = (place,targets[0][1][1])




    return sets


    

def makesets(story):
    sets = entityextract(story)
    #print("ee")
    #print([(x[0],x[1].entity,x[1].num) for x in sets])
    sets = containers(sets,story)
    #print("c")
    #print([(x[0],x[1].entity,x[1].num) for x in sets])
    #sets = circumscription(sets,story)
    sets = uc.main(sets)
    sets = add_bare_sets(sets,story)
    #print("units and bare sets")
    #print([(x[0],x[1].entity,x[1].num) for x in sets])
    sets = fix_each(sets)
    sets = fix_times(sets)
    #print('eac')
    #print([(x[0],x[1].entity,x[1].num) for x in sets])
    sets = move_x(sets,story)
    #print('mov x')
    #print([(x[0],x[1].entity,x[1].num) for x in sets])
    #print([(x[0],x[1].entity,x[1].num) for x in sets])
    #rewrite(sets,story)
    

    '''
    THIS CODE PRODUCES ? ENTITIES WHICH ARE NOT O.W. CAPTURED BY PREVIOUS RULES
    
    ents = set([x[1].entity for x in sets])
    idxs = [x[1].idx for x in sets]
    for j,s in enumerate(story):
        deps = s['indexeddependencies']
        lemmas = [x[1]["Lemma"] for x in s['words']]
        for e in ents:
            for i,l in enumerate(lemmas):
                if l == e:
                    eidx = j*1000+i
                    if eidx in idxs:
                        # this occurrence is already accounted for
                        continue
                    else:
                        print(j*1000+i)
                        surface = s['words'][i][0]
                        edeprep = surface+'-'+str(i+1)
                        edep = [x[2].split("-")[0] for x in deps if x[1] == edeprep and x[0] == 'det']
                        if edep:
                            num = edep[0]
                        else:
                            num = "?"
                        sets.append(((j*1000)+i,aset(num,l,surface,j*1000+i)))
    '''
    
    i=0
    #print(sets)
    while i < len(sets):
        x = sets[i]
        if (not floatcheck(x[1].num)) and x[1].num != 'x':
            sets.remove(x)
        else:
            i+=1

    #print(sets)
    '''
    i = 0
    while i < len(sets):
        x = sets[i]
        dups = [y for y in sets if y[0]==x[0]]
        if len(dups)>1:
            #print("dups ",dups); exec(input());input()
            for y in dups[:-1]:
                sets.remove(y)
        i+=1
    '''
        
    #fix idx
    for idx,x in sets:
        x.idx = idx
    try:
        sets = sorted(sets)               
    except:
        #print(sets)
        #exec(input())
        pass

    return sets

class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

def bug():
    print("bug")
    ip = 0
    while ip==0:
        inp = input()
        if inp == 0:
            ip=1
        else:
            exec(inp)

if __name__ == "__main__":
    nlp = StanfordNLP()
    wps = open(sys.argv[1]).readlines()
    wps = list(reversed(wps))
    for k in range(len(wps)):
        print(k)
        problem = wps[k].lower()
        print(problem)
        story = nlp.parse(problem)
        sets = makesets(story["sentences"])

        for x in sets:
            x[1].details()
        if len(sets)<2:
            print("few sets")
            bug()
        input()

        sets = [x[1] for x in sets]
        nums = [x.num for x in sets]
        if 'x' not in nums:
            bug()



