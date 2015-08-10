out = open('emnlp.reduced.kushformat.txt','w')
with open('emnlp.reduced.eq_pr.txt') as f:
    f = f.readlines()
    with open('emnlp.reduced.eq_answ.txt') as g:
        g = g.readlines()
        j=0
        for ans in g:
            a = ans.strip()
            p = f[j]
            j+=1
            e = f[j]
            j+=1
            tst = e.replace('x',str(a))
            a,b = tst.split("=")
            print(j)
            print(a,b)
            if eval(a)-eval(b)>0.0001:
                input()
            out.write(p)
            out.write(e)
            out.write(ans)

        
