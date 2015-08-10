from __future__ import division
import pickle
from matplotlib import pyplot

p = [[],[],[]]
r = [[],[],[]]
ls,gs,ms = pickle.load(open("thresh0.pickle2",'rb'))
ls2,gs2,ms2 = pickle.load(open("thresh1.pickle2",'rb'))
ls = ls+ls2
gs = gs+gs2
ms = ms+ms2
for i,c in enumerate([ls,gs,ms]):
    for t in [0.9,0.8,0.7,0.6,0.5,0.4,0.3,0.1,0.0]:
        ts = [x for x in c if x[0]>t]
        print(ts)
        if not ts: p[i].append(0);r[i].append(0)
        else:
            r[i].append(len([x for x in ts if x[2]==1])/106);p[i].append(len([x for x in ts if x[2]==1])/len(ts))

print(p,r)
for i in range(len(p)):
    pyplot.plot(r[i],p[i])

pyplot.show()

