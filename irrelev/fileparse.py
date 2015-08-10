from EntitySet import EntitySet 
from Problem import Problem

def getDataFromFile(file):
    problems = []
    openedFile = open(file)
    entities = []
    index = -1
    for line in openedFile:
        if line.__contains__('Index'):
            if index >= 0:
                problems.append(Problem(entities, answer, index))
                entities = []
            index += 1
        elif line.__contains__('Answer:'):
            answer = line.split('Answer: ')[1].replace(',','')
            if answer.__contains__("/"):
                answer = replace(answer)
            if len(answer.split()) > 1:
                ans = 0.0
                for a in answer.split():
                    ans += float(a)
                answer = ans
            answer = float(answer)
        elif line.__contains__('adjs :'):
            adj = line.split('adjs : ')[1:]
            for a in range(len(adj)):
                adj[a] = adj[a].strip()
            temp = adj[:]
            adj = []
            for a in range(len(temp)):
                if (temp[a] is not 'many') and (temp[a] is not 'more') and (temp[a] is not 'much'):
                    adj.append(temp[a])
        elif line.__contains__('entity :'):
            ent = line.split('entity : ')[1].strip()
        elif line.__contains__('num :'):
            num = line.split('num : ')[1].strip()
            if num is not 'x':
                if num.__contains__("/"):
                    num = replace(num)
                num = float(num.replace(',', ''))
        elif line.__contains__('widx'):
            entities.append(EntitySet(adj, ent, num))
    problems.append(Problem(entities, answer, index))
    return problems

def replace(ex):
    frac = ex.split("/")
    c1 = frac[0].split()
    end = getEnd(c1)
    for curr in frac[1:]:
        c2 = curr.split()
        front = getFront(c2)
        string = end + "/" + front
        val = float(sum(Fraction(s) for s in string.split()))
        ex = ex.replace(string, str(val))
        end = getEnd(c2)
    f = ex.split()
    ex = 0
    for val in f:
        ex += float(val)
    return ex

def getFront(c):
    front = c[0]
    if(len(c)>2 and c[1].isdigit()):
        front = c[1] + " " + front
    return front

def getEnd(c):
    end = c[len(c)-1]
    if(len(c) > 2 and c[len(c)-2].isdigit()):
        end = c[len(c)-2] + " " + end
    return end
