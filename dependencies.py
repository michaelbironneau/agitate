#Dependency manager
#------------------
#Purpose: To assess which models depend on a file and to send UPDATE requests
#to the API if the files change, even if the model content itself doesn't
#One can have interdependency between models, i.e. it's possible to
#have a folder structure of the form:
#-/model1s
#-/model2s
#-/dependencies
#
#It is also possible to have a folder structure of the form
#-/model1s
#  -model1a.yaml
#  -model2b.yaml
#  -...
#  -/dependencies
#-/model2s
#  -model2a.yaml
#  -model2b.yaml
#  -...
#  -/dependencies
import glob
import yaml
import string
import os.path


class Dependencies(object):
    "Monitor dependencies of textual models and file uploads"


def __init__(self, Model=None):
    #Note: WorkingPath should NOT end with trailing slash
    self.Model = Model  # Model name
    self.Models = glob.glob(self.Model + "s/*.yaml")  # Model contents
    self.DepList = []  # Todo: Is this line necessary?
    LoadDependencies()

    #Returns a list of dependent models, given an absolute file path f
    #Do this from the cache, or, if no cache is available, construct one
    def getDependentModels(f):
        #We should have dependencies in self.DepList as this was loaded in __init__
        #f is path relative to base repo, whereas paths in cache are relative to
        #model content. Therefore we need to subtract the first part of the path
        DependentModels = []
        index = string.find(f, "/")
        SearchStr = f[index + 1:]
        for model, dependency_list in self.DepList.iteritems():
            for d in dependency_list:
                if d == SearchStr:
                    DependentModels.append(model)

    def LoadDependencies():
        if os.path.isfile(self.Model + "s/" + self.Model + ".dependencies"):
            try:
                depstream = open(self.Model + "s/" + self.Model + ".dependencies", "r")
                #Safe_load, being a little paranoid here as this should be a trusted file
                deps = yaml.safe_load(depstream)
            except:
                self.DepList = UpdateDependencyCache()
        else:
            self.DepList = UpdateDependencyCache()

    #Stores dependencies of all models, needed if they change before next commit!
    def UpdateDependencyCache():
        ThisCache = []
        for m in self.Models:
            ThisCache[m] = GetFiles(m)
        try:
            f = open(self.Model + "s/" + self.Model + ".dependencies")
            f.write(yaml.dump(ThisCache))
            return ThisCache
        except:
            "Error writing file dependency cache for " + self.Model + "s"

    #Get list of files that model f depends on
    #Assume: path of f is valid and exists
    def GetFiles(f):
        FileList = []
        try:
            stream = open(f, "r")
            try:
                model = yaml.load(stream)
            except yaml.YAMLEerror, exc:
                if hasattr(exc, "problem_mark"):
                        mark = exc.problem_mark
                        print("Error parsing file " + f)
                        print("Error location: (%s:%s)") % (mark.line + 1, mark.column + 1)
        except:
            print("Error reading file " + f)
            return ""
        for k in model:
            if "@file(" in k:
                FileList.append(self.GetRelPath(k))
            elif "@content(" in k:
                FileList.append(self.GetRelPath(k))
        return filter(len, FileList)

    #Parses line to return working path
    def GetRelPath(line):
        closing = string.rfind(line, ")") - 1
        if closing == -2:
            print "Missing )"
            return ""
        if "@file(" in line:
            temp = string.replace(line, "@file(", "")
        elif "@content(" in line:
            temp = string.replace(line, "@content(", "")
        relpath = string.strip(temp[1:closing])
        if len(relpath) == 0:
            print "File path appears to be empty!"
        return relpath
