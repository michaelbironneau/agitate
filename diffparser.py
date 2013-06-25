#Doesn't work yet
from dependencies import Dependencies
import string
import os.path


class DiffParser(object):
    def __init__(self, input=None, models=None):
        lines = string.split(input, "\n")
        self.files = {}
        self.dependencies = {}
        self.Models = models
        #Get status of all files that have been modified in
        #dictionary form for convenience
        for f in lines:
            line = string.split(f, "       ")
            self.files[line[0]] = string.strip(line[1])
        for m in self.Models:
            self.dependencies[m] = Dependencies(m)

    def getCreates(self):
        Creates = []
        for k, v in self.files.iteritems():
            if k == "A":  # Added files
                #Isolate model files
                #1: Check in model directories
                for m in self.Models:
                    if string.find(v, m + "s/") == 0 and os.path.splitext(v)[1] == ".yaml":
                        Creates.append(v)
                        break
        return Creates

    def getUpdates(self):
        #Make sure to use dependencies to generate additional
        #updates caused by dependent file changes
        Updates = []
        for k, v in self.files.iteritems():
            if k == "M":  # Modified files
                #Isolate model files
                #1: Check in model directories
                for m in self.Models:
                    if string.find(v, m + "s/") == 0 and os.path.splitext(v)[1] == ".yaml":
                        Updates.append(v)
                        break
                #Do any models depend on the modified file? If so they need updating.
                modelname = v[0:string.find(v, "s/")]
                dependents = self.dependencies[modelname].getDependentModels(v)
                if len(dependents) > 0:
                    Updates += dependents
        return Updates

    def getDeletes(self):
        Deletes = []
        for k, v in self.files.iteritems():
            if k == "D":  # Deleted files
                #Isolate model files
                #1: Check in model directories
                for m in self.Models:
                    if string.find(v, m + "s/") == 0 and os.path.splitext(v)[1] == ".yaml":
                        Deletes.append(v)
                        break
        return Deletes
