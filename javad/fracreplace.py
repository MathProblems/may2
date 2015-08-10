import sys

with open("emnlp.problems.txt") as f:
    with open("emnlp.problems.frac.txt",'w') as g:

        for line in f:
            line = line.strip().split(" ")
            for i in range(len(line)):
                if "/" in line[i]:
                    line[i] = str(eval(line[i]))
            line = " ".join(line)+'\n'
            g.write(line)

