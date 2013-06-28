#Unit tests for Dependencies

import unittest
from dependencies import Dependencies
import os
import os.path


class DepTests(unittest.TestCase):
    #Run some tests
    def setUp(self):
        self.model = 'post'
        os.chdir(os.path.join(os.getcwd(), 'example'))
        self.dependencies = Dependencies(self.model)
        self.dependencies.UpdateDependencyCache()

    def tearDown(self):
        os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    def test_ResourceLoad(self):
        self.assertEqual(len(self.dependencies.Resources), 2, 'Incorrect load - not enough resources loaded')

    def test_DepFileCreated(self):
        self.assertTrue(os.path.isfile(self.model + "s/" + self.model + ".dependencies"), 'Dependency file not created')

    def test_GetFile(self):
        f = self.dependencies.GetFiles('posts/introduction2.yaml')
        bool = (f[1] == 'Thumbnails/3.jpg' and f[0] == 'Markdown/content.md')
        self.assertTrue(bool, 'GetFile test failed')

    def test_GetRelPath1(self):
        self.assertEqual(self.dependencies.GetRelPath(' @file(this/is/a/file) '), 'this/is/a/file', '@file incorrectly parsed')

    def test_GetRelPath2(self):
        self.assertEqual(self.dependencies.GetRelPath('  @content(this/is/a/file)'), 'this/is/a/file', '@content incorrectly parsed')

    def test_FileLookup(self):
        self.assertEqual(self.dependencies.getDependentResources(self.model + 's/Markdown/content.md')[0], 'posts/introduction2.yaml')

if __name__ == '__main__':
    unittest.main()
