
import logging
import posixpath
import sys
import unittest

from unicorn import *
from deobf import cfg
from deobf.cfg import CodeBlock
from deobf.ins_helper import *
from deobf.intruction_mgr import *


class TestAsm(unittest.TestCase):

    def test_disasm(self):
        ins_mgr = IntructionManger(True)
        block = CodeBlock(0x0007CA86, 0x0007CA94)
        with open("tests/bin/libcms.so", "rb") as f:
            codes = get_block_codes(f, block, ins_mgr)
            self.assertEqual(len(codes), 4)
        #
    #
        
    def test_disasm_bb(self):
        ins_mgr = IntructionManger(True)
        with open("tests/bin/libSecShell.so", "rb") as f:
            start = 0x0001B180
            end = 0x0001DF4C
            f.seek(start, 0)
            b = f.read(end-start)
            codes = ins_mgr.disasm(b, start)
            self.assertEqual(len(codes), 4470)
        #
    #
#