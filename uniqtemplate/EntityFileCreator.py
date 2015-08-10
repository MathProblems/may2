# Code to convert the list of entities into an output file

def main(sets, index, a):
    entities = [x[1] for x in sets if x[1].num != 'x']
    entities += [x[1] for x in sets if x[1].num == 'x']
    getOutputValues(entities, index, a)


def getOutputValues(entities, index, answer):
    constants = []
    unknowns = ['x']
    objtypes = []
    constantOrUnknownType = []

    for e in entities:
        # constants
        const = ''.join([x for x in e.num if x!=','])
        constants.append(const)

        # objtypes and constantorUnknownType
        ent = e.entity
        if (ent not in objtypes):
            objtypes.append(ent)
        constantOrUnknownType.append(objtypes.index(ent))

    printOutputValues(constants, unknowns, objtypes, constantOrUnknownType, index, answer)

def printOutputValues(constants, unknowns, objtypes, constantOrUnkownType, index, answer):
    file = open('translatedEntities.1.output', 'a')
    file.write('\n'+str(index)+'\n')
    file.write('entities :')
    writeVals(file, constants)
    file.write('\n' + 'operators : + - * / =')
    file.write('\n' + 'objtypes :')
    writeVals(file, objtypes)
    file.write('\n' + 'entityType :')
    writeVals(file, constantOrUnkownType)
    file.write('\n' + 'n : ' + str((len(constants) * 2 - 1)))
    file.write('\n' + 'answer : ' + str(answer))
    

def writeVals(file, values):
    for v in values:
        file.write(' ' + str(v))


if __name__ == "__main__":
    main()
