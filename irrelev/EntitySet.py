# A single set for an entity

class EntitySet():
    def __init__(self, adj, entity, num):
        self.adj = adj
        self.entity = entity
        self.num = num

    def toString(self):
        return 'adj: ' + str(self.adj) + ', ent: ' + str(self.entity) + ', num: ' + str(self.num)