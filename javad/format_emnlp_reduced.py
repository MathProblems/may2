import sys
folder = sys.argv[1]
out = open(folder+"formatted.txt",'w')
with open(folder+'q.txt') as f:
    f = f.readlines()
    with open(folder+'ans.txt') as g:
        g = g.readlines()
        j=0
        for ans in g:
            a = ans.strip()
            p = f[j]
            e = "\n"
            j+=1
            out.write(p)
            out.write(e)
            out.write(ans)

        
