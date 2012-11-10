#!/usr/bin/python

import unittest
import sqlite3 as db
import os
import re
from tools.dbinstall import DBInstall
from lib.guardedcursor import GuardedCursor, Result
from lib.manager import Manager

class TestManager(unittest.TestCase):

	def setUp(self):
		self.unlink()

	def unlink(self):
		try:
			os.unlink("foo")
		except OSError:
			pass

	def tearDown(self):
		self.unlink()

	def test_emptydb(self):
		m = Manager("foo")
		self.assertTrue(os.path.exists("foo"))


if __name__ == '__main__':
	unittest.main()

