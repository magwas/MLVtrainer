#!/usr/bin/python

import unittest
import os
import re
import sqlite3

class DBInstall:

	def run_one(self,s,conn):
		f = open(s)
		s=f.read()
		cur = conn.cursor()
		for stmt in s.split(';'):
			cur.execute(stmt)
		conn.commit()
		cur.close()
		f.close()

	def run(self,connstring):
		conn = sqlite3.connect(connstring)
		self.run_one("schema/create.sql",conn)
		for f in sorted(os.listdir("schema")):
			if re.match("[0-9]{3}.*\.sql",f):
				self.run_one("schema/"+f,conn)
		conn.close()

if __name__ == '__main__':
	import sys
	print "creating database at %s"%sys.argv[1]
	DBInstall().run(sys.argv[1])

