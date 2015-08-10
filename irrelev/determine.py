import sys
import fileparse

prblms = fileparse.getDataFromFile('siena_output.6.1.2.txt')
irrelev = open("labels.6.1.2.txt").readlines()
unsolvable = 0 
total = 0 # total
irrelevant_count = 0
correctly_classified_irrelevant = 0
misclassified_relevant = 0
misclassified_irrelevant = 0
for prblm in prblms: 
    if irrelev[total].strip() in ["Unsolvable",'bad']:
        unsolvable+=1;total+=1; continue
    label = irrelev[total].strip() == "Irrelevant"
    irrelevant_count+=int(label)
    total+=1
    te = prblm.getTargetEntity()
    if te != None:
        alle = prblm.getEnts()
        if len(alle)>3:
            alladj = []
            adjtmp = []
            for e in prblm.entities:
                adjtmp.extend(e.adj)
            for a in adjtmp:
                alladj.extend(a.split(" "))
            for x in ['many','None','much','more','new','total']:
                alladj = [y for y in alladj if y!=x]
            if len(list(set(alladj)))>1:
                if label:
                    correctly_classified_irrelevant+=1
                else:
                    misclassified_relevant+=1
            else:
                if len(set(alle))>1:
                    if label:
                        correctly_classified_irrelevant+=1
                    else:
                        print(alle)
                        misclassified_relevant+=1
                else:
                    if label:
                        print(total)
                        print(alle)

        continue
        if te.entity.isupper():
            alle.remove(te.entity)
        if len(list(set(alle)))==1:
            tadj = te.adj
            alladj = []
            adjtmp = []
            for e in prblm.entities:
                adjtmp.extend(e.adj)
            for a in adjtmp:
                alladj.extend(a.split(" "))
            for x in ['many','None','much','more','new','total']:
                if x in alladj:
                    alladj.remove(x)
            if len(list(set(alladj)))>1:
                if label:
                    correctly_classified_irrelevant+=1
                else:
                    misclassified_relevant+=1
        else:
            if label:
                correctly_classified_irrelevant+=1
            else:
                print(total)
                print(alle)
                misclassified_relevant+=1

    else:
        if label: print(te)
print(unsolvable,total,irrelevant_count,correctly_classified_irrelevant,misclassified_relevant)

