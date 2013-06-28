#Unit tests for Requests

import unittest
import agitate
import os
import os.path


class RequestTests(unittest.TestCase):
    def setUp(self):
        os.chdir(os.path.join(os.getcwd(), 'example'))
        self.f = "posts/introduction2.yaml"
        self.config = agitate.loadConfigFile()
        self.modelname = agitate.getModelName(self.f)
        self.files, self.content = agitate.getContent(self.f, self.config)
        self.fid = agitate.getID(self.f)

    def tearDown(self):
        os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    def testFiles(self):
        for k, v in self.files.iteritems():
            with v as afile:
                content = afile.read()
                self.assertTrue(len(content) > 0)  # Not the greatest check but it will do for now
                break

    def testPut(self):
        var = agitate.updateModel(self.f)
        self.assertEqual(var, 0)

    def testPost(self):
        var = agitate.createModel(self.f)
        self.assertEqual(var, 0)

    def testDelete(self):
        var = agitate.deleteModel(self.f)
        self.assertEqual(var, 0)

if __name__ == '__main__':
    unittest.main()
