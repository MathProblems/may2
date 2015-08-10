# An problem is a collection of sets for the word problem

class Problem():
    def __init__(self, entities=[], answer=None, index=None):
        self.entities = entities
        self.index = index
        self.answer = answer
        self.target = self.getTargetEntity()

    def getTargetEntity(self):
        for e in self.entities:
            if e.num is 'x':
                return e
        return None

    def toString(self):
        tostr = str(self.index)
        i = 1
        for ent in self.entities:
            tostr +='\n' + 'ent ' + str(i) + ': ' + ent.toString()
        return tostr

    def getNumbers(self):
        numbers = []
        for ent in self.entities:
            if ent.num is not 'x':
                numbers.append(ent.num)
        return numbers

    def getEnts(self):
        ents = []
        for ent in self.entities:
            ents.append(ent.entity)
        return ents
