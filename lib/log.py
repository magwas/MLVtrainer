
import sys
from syslog import *
import inspect

openlog(sys.argv[0],LOG_PID|LOG_NDELAY|LOG_NOWAIT)

def log(priority, eventtype, subjectum, objectum, **attrs):
	attlist = []
	for (k, v) in attrs.items():
		attlist.append(" %s=%s"%(k,v))
	attstring = ",".join(attlist)
	message="event=%s, prio=%s, subject=%s, object=%s,%s"%(eventtype, priority, subjectum, objectum, attstring)
	sys.stderr.write(message+'\n')

def debug(section,level,**attrs):
	if config.debug and ((config.debug.has_key(section) and config.debug[section] >= level) or (config.debug.has_key('*') and config.debug['*'] >= level)):
		sys.stderr.write("debug/%s/%s"%(section,level),str(inspect.stack()[1][3]).strip(),str(inspect.stack()[3][4][0]).strip(),**attrs)

