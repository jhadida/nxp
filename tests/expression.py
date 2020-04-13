
import os.path as op
import unittest
import nxp

# pylint: disable=no-member

"""
To-do:
- Strings converted to Regex
- Test Set when the first item is removed from the list.
- Test Set and Seq with nested TokenList items.
"""

# ------------------------------------------------------------------------

TEST_FILE = {
    'path': op.join(op.dirname(__file__), 'text-kafka.txt'),
    'nlines': 35,
    'nchars': 2123
}

class TestWord(unittest.TestCase):
    def setUp(self):
        self.buf = nxp.FileBuffer(TEST_FILE['path'])

    def test_finditer(self):
        first_line = ['One','morning','when','Gregor','Samsa','woke','from','troubled','dreams','he','found','himself']

        for w, m in zip( first_line, nxp.Word().finditer(self.buf.cursor()) ):
            self.assertEqual( w, self.buf.between(m.beg,m.end), 'Bad match' )

# ------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
