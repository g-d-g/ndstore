import numpy as np
from PIL import Image
import urllib2
import zlib
import StringIO
import os
import sys


# We are going to build this directly on the database to avoid
# Web transfer limitations.

# include the paths
EM_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." ))
EM_UTIL_PATH = os.path.join(EM_BASE_PATH, "util" )
EM_EMCA_PATH = os.path.join(EM_BASE_PATH, "emca" )
EM_DBCONFIG_PATH = os.path.join(EM_BASE_PATH, "dbconfig" )

sys.path += [ EM_UTIL_PATH, EM_DBCONFIG_PATH, EM_EMCA_PATH ]

import emcaproj
import emcadb
import dbconfig

# load the project
projdb = emcaproj.EMCAProjectsDB()
proj = projdb.getProj ( 'kasthuri11' )
dbcfg = dbconfig.switchDataset ( proj.getDataset() )

#Load the database
db = emcadb.EMCADB ( dbcfg, proj )


_ximagesz = 10748
_yimagesz = 12896

fid = open ( "/data/formisha/bigcutout", "w" )

for zstart in range(1,1850,16):

  # read the first 

  zend = min(zstart+16,1851)
  corner = [0,0,zstart]
  resolution = 1
  dim = [ _ximagesz, _yimagesz, zend-zstart ]
  print "Corner %s dim %s." % ( corner, dim )
  cube = db.cutout ( corner, dim, resolution )

  # write it out as bytes
  print "Writing to file"
  cube.data.tofile(fid)
  print "Writing complete"




