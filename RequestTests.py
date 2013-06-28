#Unit tests for Dependencies

import unittest
import agitate
import os
import os.path
import requests
import json


class AgTests(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.join(os.getcwd(), 'example'))
        self.f = "posts/introduction2.yaml"
        self.config = agitate.loadConfigFile()
        self.modelname = agitate.getModelName(self.f)
        self.files, self.content = agitate.getContent(self.f, self.config)
        self.fid = agitate.getID(self.f)

    def testFiles(self):
        for k, v in self.files.iteritems():
            with v as afile:
                content = afile.read()
                self.assertTrue(len(content) > 0)  # Not the greatest check but it will do for now
                break

    def tearDown(self):
        os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    def testPut(self):
        if "PUT" in self.config["Site"]["HTTP verbs"]:
            r = requests.request(method="PUT", url=self.config["Site"]["Host"] + "/" + self.modelname + "s/" + self.fid,
                                 files=self.files, data=self.content)
            self.assertEqual(r.text, "Cool beans")

    def testPost(self):
        if "Create URL" in self.config["Site"]:
            r = requests.post(self.config["Site"]["Host"] + "/" +
                              self.modelname + "s/" + self.config["Site"]["Create URL"],
                              files=self.files, data=self.content)
        else:
            r = requests.post(self.config["Site"]["Host"] + "/" +
                              self.modelname + "s",
                              files=self.files, data=self.content)
        self.assertEqual(agitate.getIDfromResponse(json.loads(r.text.decode('utf-8'))[0]), 1234)

    def testDelete(self):
        self.files, self.content = agitate.getContent(self.f, self.config, True)
        if "DELETE" in self.config["Site"]["HTTP verbs"]:
            r = requests.delete(self.config["Site"]["Host"] + "/" + self.modelname + "s/" + self.fid,
                                data=self.content)
            self.assertEqual(r.text, "Cool beans")

if __name__ == '__main__':
    unittest.main()
