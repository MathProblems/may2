# Code to convert the list of entities into an output file

def main(sets, index,answ):
    entities = [x[1] for x in sets if x[1].num != 'x']
    entities += [x[1] for x in sets if x[1].num == 'x']
    getOutputValues(entities, index,answ)

def getTempEntities():
    entities = []
    entities.append(EntityTemp('seashell', '70'))
    entities.append(EntityTemp('seashell', 'x'))
    entities.append(EntityTemp('seashell', '27'))
    return entities

def getOutputValues(entities, index,answ):
    constants = []
    unknowns = []
    objtypes = []
    constantOrUnknownType = []

    for e in entities:
        # constants
        if (e.num != 'x'):
            constants.append(e.num)
        else:
            unknowns.append('x')

        # objtypes and constantorUnknownType
        ent = e.entity
        if (ent not in objtypes):
            objtypes.append(ent)
        constantOrUnknownType.append(objtypes.index(ent))

    printOutputValues(constants, unknowns, objtypes, constantOrUnknownType, index,answ)

def printOutputValues(constants, unknowns, objtypes, constantOrUnkownType, index,answ):
    file = open('translatedEntities.output', 'a')
    file.write('\n'+str(index)+'\n')
    file.write('constants :')
    writeVals(file, constants)
    file.write('\n' + 'unknowns :')
    writeVals(file, unknowns)
    file.write('\n' + 'operators : + - * / =')
    file.write('\n' + 'objtypes :')
    writeVals(file, objtypes)
    file.write('\n' + 'constantOrUnknownType :')
    writeVals(file, constantOrUnkownType)
    file.write('\n' + 'n : ' + str((len(constants) * 2 + 1)))
    file.write('\nanswer : ' + str(answ))
    file.write('\n')

def writeVals(file, values):
    for v in values:
        file.write(' ' + str(v))


if __name__ == "__main__":
    main()
