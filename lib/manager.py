#!/usr/bin/python

import sqlite3 as db
import sys
import os
import random
import subprocess
from lib.guardedcursor import GuardedCursor
from tools.dbinstall import DBInstall


class UI:
	@staticmethod
	def clear():
		os.system([ 'clear', 'cls' ][ os.name == 'nt' ] )

	@staticmethod
	def say(ans,language,encoding='latin-1'):
		p=subprocess.Popen(['festival' ,'--language', language, '--tts'],stdin=subprocess.PIPE).stdin
		p.write(ans.encode(encoding))
		p.close()

	@staticmethod
	def getans():
		ans=sys.stdin.readline().strip()
		return ans.decode('utf-8')

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

	def cmd_train(self,cmd):
		"""
		Train a category
		"""
		with GuardedCursor(self.con) as cur:
			self.cmd_lscat(None)
			print "which categories to learn? (comma separated)"
			catlist=UI.getans()
			rr = cur.execute("select lang1translation as l1,lang2translation as l2 from vocabulary where categoryid in (%s)"%catlist)
			wlist = []
			for r in cur.generator():
				wlist.append([r.l1,r.l2,0])
		UI.clear()
		while True:
			i = random.randint(0,len(wlist)-1)
			o = wlist[i]
			print "\n",o[0]
			UI.say(o[0],language='english')
			ans=UI.getans()
			if o[1] == ans:
				o[2] += 1
			else:
				while ans != o[1]:
					print o[1]
					UI.say(o[1],language="spanish")
					ans=UI.getans()
			print "correct!", o[2]
			UI.say(o[1],language="spanish")
			if o[2] > 3:
				wlist.remove(o)
				print "learned:",o[0],o[1]
			if len(wlist) == 0:
				break
			ans=UI.getans()
			if ans == 'quit':
				return
			UI.clear()
		

	def cmd_help(self,dummy=None):
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

