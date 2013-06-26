#Unit tests for Dependencies

import unittest
import agitate
import os
import os.path
import yaml


class AgTests(unittest.TestCase):
    #Run some tests
    def setUp(self):
        os.chdir(os.path.join(os.getcwd(), 'example'))

    def tearDown(self):
        os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    def test_Config(self):
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
            self.assertEqual(agitate.CheckConfig(config), 0, "Config malformed")
        except yaml.YAMLError, exc:
            print "Error processing config file."
            if hasattr(exc, "problem_mark"):
                mark = exc.problem_mark
                print("Error location: (%s:%s)") % (mark.line + 1, mark.column + 1)

    def test_ModelName(self):
        self.assertEqual(agitate.getModelName("posts/post1234.yaml"), "post")

    def test_getContentFiles(self):
        files, variables = agitate.getContent("posts/introduction2.yaml")
        self.assertEqual(len(files), 2)  # This isn't enough to guarantee a good request

    def test_getContentVars(self):
        files, variables = agitate.getContent("posts/introduction2.yaml")
        self.assertEqual(variables["slug"], "this-is-a-slug")

    def test_getIDs(self):
        self.assertEqual(agitate.getID("posts/introduction2.yaml"), "1234")

    def test_updateIDs(self):
        agitate.updateID("posts/introduction2.yaml", "2345")
        self.assertEqual(agitate.getID("posts/introduction2.yaml"), "2345")
        agitate.updateID("posts/introduction2.yaml", "1234")

    def test_deleteID(self):
        agitate.deleteID("posts/introduction2.yaml")
        self.assertEqual(agitate.getID("posts/introduction2.yaml"), None)
        agitate.updateID("posts/introduction2.yaml", "1234")

    def test_getIDfromResp(self):
        resp_test = {}
        resp_test["key1"] = "1234b"
        resp_test["key2"] = "3151"
        self.assertEqual(agitate.getIDfromResponse(resp_test), "3151")

    #Additional test to make sure that multiple lines in file are handled OK
    #due to different creation/update mechanisms.
    #--Maybe unecessary now that createID and updateID have been merged--
    def test_multiID(self):
        agitate.updateID("posts/introduction.yaml", "2345")
        self.assertEqual(agitate.getID("posts/introduction.yaml"), "2345")
        agitate.deleteID("posts/introduction.yaml")

if __name__ == '__main__':
    unittest.main()
