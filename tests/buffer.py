
import os.path as op
import unittest
from nxp import FileBuffer, ListBuffer

# pylint: disable=no-member

# ------------------------------------------------------------------------

TEST_FILE = {
    'path': op.join(op.dirname(__file__), 'text-kafka.txt'),
    'nlines': 35,
    'nchars': 2123
}

class TestFileBuffer(unittest.TestCase):
    def setUp(self):
        self.buf = FileBuffer(TEST_FILE['path'])

    def test_properties(self):
        self.assertEqual( len(self.buf), TEST_FILE['nlines'], 'Problem with __len__' )
        self.assertEqual( self.buf.nlines, TEST_FILE['nlines'], 'Problem with nlines' )
        self.assertEqual( self.buf.nchars, TEST_FILE['nchars'], 'Problem with nchars' )

class TestListBuffer(unittest.TestCase):
    def setUp(self):
        with open(TEST_FILE['path']) as fh:
            self.buf = ListBuffer(list(fh))

    def test_properties(self):
        self.assertEqual( len(self.buf), TEST_FILE['nlines'], 'Problem with __len__' )
        self.assertEqual( self.buf.nlines, TEST_FILE['nlines'], 'Problem with nlines' )
        self.assertEqual( self.buf.nchars, TEST_FILE['nchars'], 'Problem with nchars' )

# ------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
