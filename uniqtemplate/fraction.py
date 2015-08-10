from fractions import Fraction
# round to three decimal places

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

f = open("emnlp.answers.txt").readlines()
g = open("emnlp.answers.frac.txt",'w')
for line in f:
    if " " in line:
        line = line.strip().split(" ")
        slashes = [x for x in line if '/' in x]
        if slashes:
            m = replace(slashes[0])
            line = str(float(line[0])+float(m))
        else:
            line = line[0]
        line = line + '\n'
    else:
        line = replace(line)
    g.write(line)
