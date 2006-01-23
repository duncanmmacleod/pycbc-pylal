#!/usr/bin/python

import os
import popen2

from glue import lal
from glue import LSCsegFindClient
from glue import segments
from glue import segmentsUtils

#
# Some info
#

s5start = lal.LIGOTimeGPS(815155213)


#
# How to run tconvert
#

class TconvertCommand(object):
	def __init__(self, tspec = None):
		self._exec = "/home/kipp/local/bin/lalapps_tconvert"
		self.tspec = tspec

	def __str__(self):
		s = self._exec
		if self.tspec:
			s += " \"" + self.tspec + "\""
		return s

def runtconvert(command):
	if type(command) != TconvertCommand:
		raise ValueError, "invalid argument to runtconvert(command): command must type TconvertCommand"
	child = popen2.Popen3(str(command), True)
	for line in child.childerr:
		pass
	for line in child.fromchild:
		result = line
	status = child.wait()
	if not os.WIFEXITED(status) or os.WEXITSTATUS(status):
		raise Exception, "failure running \"" + str(command) + "\""
	return result


#
# Trigger file segment lists
#

class TrigSegs(object):
	def __init__(self):
		self.G1 = segmentsUtils.fromlalcache(file("G1/filelist.cache"), coltype = lal.LIGOTimeGPS).coalesce()
		self.H1 = segmentsUtils.fromlalcache(file("H1/filelist.cache"), coltype = lal.LIGOTimeGPS).coalesce()
		self.H2 = segmentsUtils.fromlalcache(file("H2/filelist.cache"), coltype = lal.LIGOTimeGPS).coalesce()
		self.L1 = segmentsUtils.fromlalcache(file("L1/filelist.cache"), coltype = lal.LIGOTimeGPS).coalesce()

#
# Segment querying
#

class SegFindConfig(object):
	def __init__(self, host, port, instrument):
		self.host = host
		self.port = port
		self.instrument = instrument

SegFindConfigH1 = SegFindConfig("ldas.ligo-wa.caltech.edu", None, "H1")
SegFindConfigH2 = SegFindConfig("ldas.ligo-wa.caltech.edu", None, "H2")
SegFindConfigL1 = SegFindConfig("ldas.ligo-la.caltech.edu", None, "L1")

def getsegments(config, types, bounds):
	if config.port:
		client = LSCsegFindClient.LSCsegFind(config.host, config.port)
	else:
		client = LSCsegFindClient.LSCsegFind(config.host)
	list = client.findStateSegments({"interferometer" : config.instrument, "type" : types, "start" : str(int(bounds[0])), "end" : str(int(bounds[1])), "lfns" : False, "strict" : True})
	return segments.segmentlist([segments.segment(*map(lal.LIGOTimeGPS, seg)) for seg in list])

