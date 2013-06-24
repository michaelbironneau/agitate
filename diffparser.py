#Doesn't work yet
import dependencies


class DiffInfo(object):
    "Store diff info"

    def __init__(self, input=None):
        self.input = input

    def getCreates(self):
        return self.creates

    def getUpdates(self):
        #Make sure to use dependencies to generate additional
        #updates caused by dependent file changes
        return self.updates

    def getDeletes(self):
        return self.deletes
