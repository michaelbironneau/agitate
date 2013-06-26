import sys
import string
import os
import os.path
import subprocess
import requests
import yaml
import json
import traceback
from diffparser import DiffParser
from dependencies import Dependencies


def main():
    cmdargs = sys.argv[1:]
    returnargs = " ".join(cmdargs)
    if str(cmdargs[1]) == "commit":
    #This is the only case we process. If not, return control to Git immediately.
        if "--dry-run" in cmdargs:
            #Ignore this, pass straight to git
            print subprocess.check_output("git " + returnargs)
        else:
            #We need to update the API before committing the changes to remote repo.
            config = loadConfigFile()
            if config is None:
                return 0  # No need to output anything to user, it's already been done
            try:
                Parser = DiffParser(subprocess.check_output("git diff --name-status --diff-filter=[ADM]"))
                BadResponses = 0
                for f in Parser.getUpdates():
                    modelname = getModelName(f)
                    files, content = getContent(f)
                    fid = getID(f)
                    if fid is None:
                        print "No ID available to update API with for " + f + "!"
                        BadResponses += 1
                    else:
                        if "PUT" in config["site"]["HTTP verbs"]:
                            r = requests.put(config["site"]["host"] + "/" + modelname + "/" + getID(f),
                                             files=files, data=content)
                            print "Updated model " + modelname + ", response " + r.status_code
                            if r.status_code != 200:
                                BadResponses += 1
                        else:
                            r = requests.post(config["site"]["host"] + "/" +
                                              modelname + "/" + config["site"]["Update URL"],
                                              files=files, data=content)
                            print "Updated model " + modelname + ", response " + r.status_code
                            if r.status_code != 200:
                                BadResponses += 1

                for f in Parser.getDeletes():
                    #Update the API
                    modelname = getModelName(f)
                    files, content = getContent(f)
                    fid = getID(f)
                    if fid is None:
                        print "No ID available to update API with for " + f + "!"
                        BadResponses += 1
                    else:
                        if "DELETE" in config["site"]["HTTP verbs"]:
                            r = requests.delete(config["site"]["host"] + "/" + modelname,
                                                files=files, data=content)
                            print "Deleted model " + modelname + ", response " + r.status_code
                            if r.status_code == 200:
                                deleteID(f)
                            else:
                                BadResponses += 1
                        else:
                            r = requests.post(config["site"]["host"] + "/" +
                                              modelname + "/" + config["site"]["Delete URL"],
                                              files=files, data=content)
                            print "Deleted model " + modelname + ", response " + r.status_code
                            if r.status_code != 200:
                                BadResponses += 1
                for f in Parser.getCreates():
                    #Update the API
                    modelname = getModelName(f)
                    files, content = getContent(f)
                    r = requests.post(config["site"]["host"] + "/" +
                                      modelname + "/" + config["site"]["Delete URL"],
                                      files=files, data=content)
                    print "Created model " + modelname + ", response " + r.status_code
                    if r.status_code == 200:
                        updateID(f, getIDfromResponse(json.loads(r.json())))
                    else:
                        BadResponses += 1
                #Make sure that everything updated fine on server side
                if BadResponses == 0:
                    #Update dependencies
                    print "--Content was updated on server successfully--"
                    for m in config["models"]:
                        deps = Dependencies(m)
                        deps.UpdateDependencyCache()
                    #Return control to git
                    print subprocess.check_output("git " + returnargs)
                else:
                    go_on = input("There were " + BadResponses + " unsuccessful updates. Commit repository anyway (y/n)?")
                    if go_on == "y":
                        for m in config["models"]:
                            deps = Dependencies(m)
                            deps.UpdateDependencyCache()
                        #Return control to git
                        print subprocess.check_output("git " + returnargs)
                    else:
                        return 0
            except subprocess.CalledProcessError:
                print "Error invoking git diff"
    else:
        #If this isn't a commit, there's nothing to update
        print subprocess.check_output("git " + returnargs)


#Checks that the config file has the required sections, once it has been
#successfully validated as valid YAML.
def CheckConfig(config):
    if not "Site" in config:
        print "Config file must have a 'Site' section"
        return 1
    else:
        if not "host" in config["Site"]:
            print "Config file must specify host"
            return 1
        if "HTTP verbs" in config["Site"]:
            #Is it necessary to force the user to write this every time?
            #For the sake of brevity in config file, might be better
            #to systematically omit GET/POST since any API will
            #obviously allow them.
            if not "GET" in config["Site"]["HTTP verbs"]:
                print "GET method must be allowed."
            if not "POST" in config["Site"]["HTTP verbs"]:
                print "POST method must be allowed."
        else:
            print "Config file must specify allowed HTTP verbs"
            return 1

        return 0


def getModelName(f):
    return f[0:string.find(f, "s/")]


#Gets JSON-formatted content of file including
#Looking for external dependencies
#Automatically returns id if it is available
def getContent(f):
    files = {}
    variables = {}
    modelname = f[0:string.find(f, "s/")]  # Got two methods for determining
    #model names, not equivalent. This is not  a great idea!
    dependents = Dependencies(modelname)
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
        if "@file(" in v or "@content(" in v:
            files[k] = open(os.path.join(os.getcwd(), modelname + "s/", dependents.GetRelPath(v)), "rb")
        else:
            variables[k] = v
    return files, variables


def loadConfigFile():
     #First, make sure that config options are here and well-formed
    if os.path.isfile("agitate.yaml"):
        configpath = "agitate.yaml"
    elif os.path.isfile(".agitate"):
        configpath = ".agitate"
    else:
        print("Cannot find agitate configuration file.")
        return None
    try:
        with open(configpath, "r") as configstream:
            #Safe_load as we don't know that user won't use untrusted config file
            config = yaml.safe_load(configstream)
        if CheckConfig(config) == 1:  # Failed config test, quit
            return None
    except yaml.YAMLError, exc:
        print "Error processing config file."
        if hasattr(exc, "problem_mark"):
            mark = exc.problem_mark
            print("Error location: (%s:%s)") % (mark.line + 1, mark.column + 1)
        return None
    except:
        print "Error accessing config file"
        return None
    return config


#Appends a resource's id to corresponding ID file after creation
#It's not really necessary to include the model since that
#can be interred from the key, but it's available to the
#calling method anyway so it saves some overhead.
#
#TODO: Replace YAML parser by own routine, it will probably be
#a bit faster and we don't require the power of YAML to parse
#this simple file format
#Note: Will create the key if not available
#Note2: In theory, the id of a model does not need to be updated
#but maybe we should account for this anyway?
def updateID(f, value):
    model = getModelName(f)
    idfilepath = model + "s/" + model + ".ids"
    if os.path.isfile(idfilepath):
        try:
            #No foreseeable race conditions, we can read/write in
            #two separate goes
            with open(idfilepath, "r") as afile:
                ids = yaml.safe_load(afile)
                ids[f] = value
            with open(idfilepath, "w") as afile:
                afile.write(yaml.dump(ids))
        except:
            print "Error writing to ID file, please check folder permissions?"
    else:
        try:
            line = f + ": " + value
            with open(idfilepath, "w") as afile:
                afile.write(line)
        except:
            print "Error writing to ID file, please check folder permissions"


#Gets resource ID from the filename
def getID(f):
    model = getModelName(f)
    idfilepath = model + "s/" + model + ".ids"
    if os.path.isfile(idfilepath):
        try:
            with open(idfilepath, "r") as afile:
                ids = yaml.safe_load(afile)
            if f in ids:
                return ids[f]
            else:
                return None
        except:
            print "Error writing to ID file, please check folder permissions?"


def deleteID(f):
    model = getModelName(f)
    idfilepath = model + "s/" + model + ".ids"
    if os.path.isfile(idfilepath):
        try:
            #No foreseeable race conditions, we can read/write in
            #two separate goes
            with open(idfilepath, "r") as afile:
                ids = yaml.safe_load(afile)
                if f in ids:
                    del ids[f]
            with open(idfilepath, "w") as afile:
                afile.write(yaml.dump(ids))
        except:
            print "Error writing to ID file, please check folder permissions?"
    else:
        print "Warning: no id file to delete from!"


#Gets ID from response.
#This is the value of the first numeric key in resp
def getIDfromResponse(resp):
    for key, value in resp.iteritems():
        if value.isdigit():
            return value
    return None


if __name__ == "__main__":
    main()
