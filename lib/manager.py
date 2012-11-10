#!/usr/bin/python

import sqlite3 as db
import sys
import os
from lib.guardedcursor import GuardedCursor
from tools.dbinstall import DBInstall



class Manager:

	def __init__(self,dbpath):
		self.con = db.connect(dbpath)
		self.curcat = None
		with GuardedCursor(self.con) as cur:
			try:
				cur.execute("select * from categories")
			except db.OperationalError:
				DBInstall().run(dbpath)
				self.con.commit()

	def mainloop(self):
		while True:
			sys.stdout.write(">")
			line = sys.stdin.readline().strip()
			line = line.split(' ')
			cmd = 'cmd_'+line[0]
			if cmd in dir(self):
				getattr(self,cmd)(line)
			else:
				self.cmd_help()

	def cmd_help(self):
		"gives help"
		for i in dir(self):
			if i[:4] == 'cmd_':
				print "%s : %s"%(i[4:], getattr(self,i).__doc__)

	def cmd_lscat(self, cmd):
		"""lists available categories """
		with GuardedCursor(self.con) as cur:
			cur.execute("select * from categories")
			for r in cur.generator():
				print "%s : %s"%(r.id,r.category)

	def cmd_cc(self,cmd):
		"""changes current category
	usage: cc [<name>]
	if name not given, then prints the current category
	"""
		#FIXME: inut validation missing
		if len(cmd) >=2:
			self.curcat = cmd[1]
		print self.curcat

	def cmd_add(self,cmd):
		"""adds vocabulary to the current category
	waits for lines in the form
	<expression in language 1>:<expression in language 2>
	stops with the first line not containing ':'
	"""
	
		with GuardedCursor(self.con) as cur:
			while True:
				sys.stdout.write("vocab entry>")
				line = sys.stdin.readline().split(':')
				if len(line) < 2:
					return
				l1=line[0].strip()
				l2=line[1].strip()
				#FIXME: this insert is broken
				cur.execute("insert into vocabulary select id, '%s', '%s' from categories where category = '%s'"%(l1,l2,self.curcat))
				self.con.commit()
				

	def cmd_ls(self,cmd):
		"""lists vocabulary in current category"""
		with GuardedCursor(self.con) as cur:
			cur.execute("select v.lang1translation, v.lang2translation from categories c, vocabulary v where c.id=v.categoryid and c.category='%s'"%(self.curcat,))
			for v in cur.generator():
				print "%s : %s"%(v.lang1translation, v.lang2translation)
	
	def cmd_quit(self,cmd):
		"""quits"""
		sys.exit(0)

	def cmd_addcat(self,cmd):
		"""adds category
	usage: addcat <name>
		"""
		#FIXME: more validation needed (already existing name, strange characters
		with GuardedCursor(self.con) as cur:
			cur.execute("select max(id)  as id from categories")
			maxid=cur.generator().next().id
			if maxid is None:
				maxid = 0
			else:
				maxid = int(maxid)
			cmd = "insert into categories (id, category) values (%s,'%s')"%(maxid+1,cmd[1])
			print cmd
			cur.execute(cmd)
			self.con.commit()
		self.cmd_lscat(None)
		

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "usage: manager <filename>"

	Manager(sys.argv[1]).mainloop()

