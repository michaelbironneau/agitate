import sys
from os import sep
import os.path
import subprocess
import diffparser
import requests
import yaml
from dependencies import Dependencies


def main():
    cmdargs = sys.argv[1:]
    returnargs = " ".join(cmdargs)
    if str(cmdargs[1]) == "commit":
    #This is the only case we process. If not, return control to Git immediately.
        if "--dry-run" in cmdargs:
            #Ignore this, pass straight to git
            subprocess.check_output("git " + returnargs)
        else:
            #We need to update the API before committing the changes to remote repo.
            #First, make sure that config options are here and well-formed
            if os.path.isfile("agitate.yaml"):
                configpath = "agitate.yaml"
            elif os.path.isfile(".agitate"):
                configpath = ".agitate"
            else:
                print("Cannot find agitate configuration file.")
                return 0
            try:
                configstream = open(configpath, "r")
                #Safe_load as we don't know that user won't use untrusted config file
                config = yaml.safe_load(configstream)
                if CheckConfig(config) == 1:  # Failed config test, quit
                    return 0
            except yaml.YAMLEerror, exc:
                print "Error processing config file."
                if hasattr(exc, "problem_mark"):
                    mark = exc.problem_mark
                    print("Error location: (%s:%s)") % (mark.line + 1, mark.column + 1)
            finally:
                return 0
            try:
                Parser = diffparser(subprocess.check_output("git diff --name-status --diff-filter=[ADM]"))
                for f in Parser.getUpdates():
                    modelname = GetModelName(f)
                    files, content = getContent(f)
                    if "PUT" in config["site"]["HTTP verbs"]:
                        r = requests.put(config["site"]["host"] + "/" + modelname,
                                         files=files, data=content)
                    else:
                        r = requests.post(config["site"]["host"] + "/" +
                                          modelname + "/" + config["site"]["Update URL"],
                                          files=files, data=content)
                for f in Parser.getDeletes():
                    #Update the API
                    modelname = GetModelName(f)
                    files, content = getContent(f)
                    if "DELETE" in config["site"]["HTTP verbs"]:
                        r = requests.delete(config["site"]["host"] + "/" + modelname,
                                            files=files, data=content)
                    else:
                        r = requests.post(config["site"]["host"] + "/" +
                                          modelname + "/" + config["site"]["Delete URL"],
                                          files=files, data=content)
                for f in Parser.getCreates():
                    #Update the API
                    modelname = GetModelName(f)
                    files, content = getContent(f)
                    r = requests.post(config["site"]["host"] + "/" +
                                      modelname + "/" + config["site"]["Delete URL"],
                                      files=files, data=content)
                #Return control to git
                subprocess.check_output("git " + returnargs)
            except subprocess.CalledProcessError:
                print "Error invoking git diff"
    else:
        #If this isn't a commit, there's nothing to update
        print subprocess.check_output("git " + returnargs)


#Checks that the config file has the required sections, once it has been
#successfully validated as valid YAML.
def CheckConfig(config):
    if "site" in config:
        print "Config file must have a 'site' section"
        return 1
    else:
        if not "host" in config["site"]:
            print "Config file must specify host"
            return 1
        if "HTTP verbs" in config["site"]:
            #Is it necessary to force the user to write this every time?
            #For the sake of brevity in config file, might be better
            #to systematically omit GET/POST since any API will
            #obviously allow them.
            if not "GET" in config["site"]["HTTP verbs"]:
                print "GET method must be allowed."
            if not "POST" in config["site"]["HTTP verbs"]:
                print "POST method must be allowed."
        else:
            print "Config file must specify allowed HTTP verbs"
            return 1

        return 0


#Gets model name from filename.
def GetModelName(f):
    dirname = str.split(os.path.dirname(f, os.sep))[:-2]
    if dirname[-1:] == "s":
        #All's good, the directory name is a plural of the model name, so return that
        return dirname[0:-1]
    else:
        #Assume directory name IS the model name. Return a warning to that effect
        print "Warning: No plural detected in directory name '" + dirname + \
            "'. Assuming it's the model name."
        return dirname


#Gets JSON-formatted content of file including
#Looking for external dependencies
#Automatically returns id if it is available
def GetContent(f):
    files = {}
    variables = {}
    modelname = f[0:string.find(f, "s/")] #Got two methods for determining
    #model names, not equivalent. This is not  a great idea!
    dependencies = Dependencies(modelname)
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
    for k,v in model.iteritems():
        if "@file(" in v or "@content(" in v:
            files[k] = open(os.path.join(os.getcwd(), modelname + "s/", Dependencies.GetRelPath(v)), "rb")
        else:
            variables[k] = v
    return files, variables


if __name__ == "__main__": main()
