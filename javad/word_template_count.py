import sys
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

def uniq_words(q):
    wrds = ' '.join([x.lower() for x in q]).split(" ")
    return (len(wrds),len(set(wrds)))

def uniq_templ(e):
    temps = []
    for x in e:
        t = ''.join([y for y in x if y in "()=+-*/"])
        temps.append(t)
    return len(set(temps))




if __name__=='__main__':
    inp = sys.argv[1]
    q,a,e = parse_inp(inp)
    w,u = uniq_words(q)
    t = uniq_templ(e)
    print(w,u,t)


