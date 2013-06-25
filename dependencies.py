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
import sys
import traceback


class Dependencies(object):
    def __init__(self, Model):
        #Note: WorkingPath should NOT end with trailing slash
        self.Model = Model  # Model name
        self.Models = glob.glob(self.Model + "s/*.yaml")  # Model contents
        self.DepList = []  # Todo: Is this line necessary?
        self.LoadDependencies()

    #Returns a list of dependent models, given an absolute file path f
    #Do this from the cache, or, if no cache is available, construct one
    def getDependentModels(self, f):
        #We should have dependencies in self.DepList as this was loaded in __init__
        #f is path relative to base repo, whereas paths in cache are relative to
        #model content. Therefore we need to subtract the first part of the path
        DependentModels = []
        index = string.find(f, "/")
        SearchStr = f[index + 1:]
        for model, dependency_list in self.DepList.iteritems():
            for d in dependency_list:
                if d == SearchStr:
                    DependentModels.append(string.replace(model, "\\", "/"))  # For readability only - not actually necessary to replace
        return DependentModels

    def LoadDependencies(self):
        if os.path.isfile(os.path.join(os.getcwd(), self.Model + "s/" + self.Model + ".dependencies")):
            try:
                depstream = open(os.path.join(os.getcwd(), self.Model + "s/" + self.Model + ".dependencies"), "r")
                #Safe_load, being a little paranoid here as this should be a trusted file
                self.DepList = yaml.safe_load(depstream)
            except:
                self.DepList = self.UpdateDependencyCache()
        else:
            self.DepList = self.UpdateDependencyCache()

    #Stores dependencies of all models, needed if they change before next commit!
    def UpdateDependencyCache(self):
        ThisCache = {}
        for m in self.Models:
            ThisCache[m] = self.GetFiles(m)
        try:
            f = open(os.path.join(os.getcwd(), self.Model + "s/" + self.Model + ".dependencies"), "w")
            f.write(yaml.dump(ThisCache))
            return ThisCache
        except:
            "Error writing file dependency cache for " + self.Model + "s"

    #Get list of files that model f depends on
    #Assume: path of f is valid and exists
    def GetFiles(self, f):
        FileList = []
        try:
            stream = file(os.path.join(os.getcwd(), f), "r")
            try:
                model = yaml.load(stream)
            except yaml.YAMLError, exc:
                if hasattr(exc, "problem_mark"):
                        mark = exc.problem_mark
                        print "Error parsing file " + f + ",", exc
                        print("Error location: (%s:%s)") % (mark.line + 1, mark.column + 1)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print "Error reading file: " + f
            print ''.join('!! ' + line for line in lines)
            return ""
        for k, v in model.iteritems():
            if "@file(" in v:
                FileList.append(self.GetRelPath(v))
            elif "@content(" in v:
                FileList.append(self.GetRelPath(v))
        return filter(len, FileList)

    #Parses line to return working path
    def GetRelPath(self, line):
        if "@file(" in line:
            temp = string.replace(line, "@file(", "")
        elif "@content(" in line:
            temp = string.replace(line, "@content(", "")
        closing = string.rfind(temp, ")")
        if closing == -1:
            print "Missing )"
            return ""
        relpath = string.strip(temp[0:closing])
        if len(relpath) == 0:
            print "File path appears to be empty!"
        return relpath
