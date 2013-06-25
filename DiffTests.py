#Unit tests for Dependencies

import unittest
from dependencies import Dependencies
import os
import os.path
from diffparser import DiffParser


class DiffTests(unittest.TestCase):
    #Run some tests
    def setUp(self):
        self.models = ['post']
        os.chdir(os.path.join(os.getcwd(), 'example'))
        with file(os.path.join(os.getcwd(), self.models[0] + "s/diff_test.txt")) as f:
            self.input = f.read()
        self.diff = DiffParser(self.input, self.models)

    def tearDown(self):
        os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    def test_Adds(self):
        self.assertEqual(self.diff.getCreates()[0], 'posts/introduction.yaml')

    def test_Updates(self):
        self.assertEqual(self.diff.getUpdates()[0], 'posts/introduction2.yaml')

    def test_Deletes(self):
        self.assertEqual(self.diff.getDeletes()[0], 'posts/introduction.yaml')

if __name__ == '__main__':
    unittest.main()
