def vec(score,guess,ogeq,integerproblem,equalsmatch,contmatch,problem):
    vec = []
    #print(score,guess,ogeq,integerproblem,equalsmatch,contmatch,problem)

    vec.append(score)
    vec.append(int(float(guess)<0))
    vec.append(int(ogeq.index("=")==1))
    vec.append(int(ogeq.index("=")==len(ogeq)-2))
    vec.append(int(ogeq[-2]=='=' and ogeq[-1]=='x'))
    if len(ogeq)>4:
        vec.append(int(ogeq[-4]=='=' and '12' in ogeq[-3:] and ogeq[-2]=="*"))
    else:
        vec.append(0)
    vec.append(equalsmatch)
    vec.append(contmatch)
    vec.append(int(integerproblem))
    vec.append(int(guess.is_integer))
    #lexical items
    vec.append(int("at first " in problem))
    vec.append(int("start " in problem))
    vec.append(int(" now " in problem))
    vec.append(int(" total " in problem))
    vec.append(int(" equally " in problem))
    vec.append(int(" equal " in problem))
    vec.append(int(" left " in problem))
    vec.append(int(" altogether " in problem))
    '''
    vec.append(int('+' in ogeq))
    vec.append(int('-' in ogeq))
    vec.append(int('*' in ogeq))
    vec.append(int('/' in ogeq))
    '''
    return vec
