
from lib.log import debug

class Result(object):

	def __init__(self, **kwargs):
		self._dict={}
		for (k,v) in kwargs.items():
			self[k] = v

	def __setitem__(self,name,value):
		if name in self.__dict__.keys():
			raise ValueError, "reserved name: %s"%(name,)
		self._dict[name] = value

	def __getitem__(self,name):
		return self._dict[name]

	def __getattr__(self,name):
		return self._dict[name]

	def keys(self):
		return self._dict.keys()

	def values(self):
		return self._dict.values()

	def __repr__(self):
		l = []
		for (k,v) in sorted(self._dict.items()):
			l.append("%s=%s"%(k,v.__repr__()))
		return "Result(%s)"%(", ".join(l))

	def __eq__(self,other):
		if sorted(self.keys()) != sorted(other.keys()):
			return False
		for (k,v) in self._dict.items():
			if other[k] != v:
				return False
		return True

class GuardedCursor(object):

	def __init__(self,con):
		self.con = con

	def __enter__(self):
		self.cur = self.con.cursor()
		return self

	def __exit__(self,type, value, traceback):
		self.cur.close()

	def dictionarize_select(self,select,ifields):
		self.cur.execute(select)
		return self.dictionarize(ifields)

	def generator(self):
		desc = map(lambda x: x[0] ,self.cur.description)
		while True:
			r = Result()
			row = self.cur.fetchone()
			if row is None:
				return
			for (n, label) in enumerate(desc):
				r[label] = row[n]
			yield r

	def dictionarize(self,ifields):
		d = {}
		for row in self.generator():
			if len(ifields) == 1:
				index = row[ifields[0]]
			else:
				index = []
				for f in ifields:
					index.append(row[f])
				index = tuple(index)
			d[index] = row
		return d

	def selectAsList(self,select):
		self.execute(select)
		r = []
		for row in self.generator():
			r.append(row.values()[0])
		return r

	def __getattr__(self,name):
		return self.cur.__getattribute__(name)
