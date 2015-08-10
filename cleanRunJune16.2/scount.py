import sys
import json
import jsonrpclib

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
class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))


if __name__=="__main__":
    nlp = StanfordNLP()
    inp = sys.argv[1]
    q,a,e = parse_inp(inp)
    s = 0
    lemmas = 0
    ulemmas = 0
    seenlemmas = []
    for qq in q:
        story = nlp.parse(qq)
        for s in story["sentences"]:
            for w in s['words']:
                if w[1]['PartOfSpeech'] in ["NN","JJ","NNS","RB","RBR","RBS","JJR","JJS","VB","VBZ","VBD","VBG","VBN","VBP"]:
                    l = w[1]["Lemma"]
                    lemmas += 1
                    if l not in seenlemmas:
                        ulemmas += 1
                        seenlemmas.append(l)



    print(lemmas,ulemmas)


        #qq = qq.strip().split(". ")
        #s += len(qq)
    #print(s)
