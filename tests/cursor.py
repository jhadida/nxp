
import re
import unittest
from nxp.read import ListBuffer, Line, Cursor

# ------------------------------------------------------------------------

TEST_TEXT = [
    "Hello world\n",
    "  With spaces before\n",
    "\tAnd tabs before and after\t\n",
    "\r\n",
    "Last line \r "
]

class TestCursor(unittest.TestCase):
    def setUp(self):
        buf = ListBuffer(TEST_TEXT)
        self.cur = Cursor( buf, 2, 7 )

    def test_line1(self):
        self.cur.setpos(0)
        pat = re.compile('hello',re.I)
        self.assertIsNotNone( self.cur.match(pat) )
        self.assertIsNotNone( self.cur.search('world') )

    def test_line3(self):
        self.cur.setpos(2,5)
        self.assertEqual( self.cur[1:4], 'And' )
        self.assertIsNone( self.cur.search('And') )
        self.assertIsNotNone( self.cur.match('tabs') )
        self.assertTrue( self.cur.line.indent == self.cur.line.post == '\t' )

    def test_line4(self):
        self.cur.setpos(3)
        self.assertTrue( self.cur.bol )
        self.assertTrue( self.cur.eol )
        self.assertTrue( self.cur.line.is_empty() )
        self.assertTrue( self.cur.line.is_white() )
        self.assertTrue( self.cur.line.uses_crlf() )

    def test_line5(self):
        self.cur.setpos(3).nextline()
        self.assertEqual( self.cur.line.post, ' ' )
        self.assertTrue( self.cur.line.is_last() )

# ------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()