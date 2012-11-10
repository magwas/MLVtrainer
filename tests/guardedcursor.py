#!/usr/bin/python

import unittest
import sqlite3 as db
import os
import re
from tools.dbinstall import DBInstall
from lib.guardedcursor import GuardedCursor, Result

cats = [
'test cat 1',
'test cat 2',
'test cat 3']

class TestGuardedCursor(unittest.TestCase):

	def setUp(self):
		self.removedb()
		DBInstall().run("testdb")
		conn = db.connect("testdb")
		with GuardedCursor(conn) as cur:
			for cmd in [
				"insert into categories values (0, 'test cat 1')",
				"insert into categories values (0, 'test cat 2')",
				"insert into categories values (0, 'test cat 3')" ]:
				cur.execute(cmd)
			conn.commit()

	def tearDown(self):
		self.removedb()

	def removedb(self):
		try:
			os.unlink("testdb")
		except OSError:
			pass

	def test_next(self):
		conn = db.connect("testdb")
		with GuardedCursor(conn) as cur:
			cur.execute("select * from categories order by id")
			n=cur.generator()
			self.assertEquals('test cat 1',n.next().category)
		conn.close()

	def test_reserved(self):
		r = Result()
		r["a"] = "b"
		self.assertEquals(r["a"],"b")
		with self.assertRaises(ValueError):
			r["_dict"] = 1
		self.assertEquals(r.keys(),["a"])
		
	def test_result(self):
		r = Result(a=2,b="3")
		self.assertEquals(r["a"],2)
		self.assertEquals(r.a,2)
		r["a"] = "b"
		self.assertEquals(r["a"],"b")
		self.assertEquals(r.a,"b")
		self.assertEquals(sorted(r.keys()),["a","b"])

	def test_selectAsList(self):
		conn = db.connect("testdb")
		with GuardedCursor(conn) as cur:
			categories = cur.selectAsList("select category from categories")
			self.assertEquals(sorted(categories), cats)

	def test_for(self):
		conn = db.connect("testdb")
		with GuardedCursor(conn) as cur:
			cur.execute("select * from categories order by id")
			s = []
			for n in cur.generator():
				s.append(n.category)
			self.assertEquals(s,cats)
		conn.close()


if __name__ == '__main__':
	unittest.main()

