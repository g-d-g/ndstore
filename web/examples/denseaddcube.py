import argparse
import empaths
import numpy as np
import urllib, urllib2
import cStringIO
import zlib
import sys

import tempfile
import h5py

def main():

  parser = argparse.ArgumentParser(description='Annotate a cubic a portion of the database.')
  parser.add_argument('baseurl', action="store" )
  parser.add_argument('token', action="store" )
  parser.add_argument('resolution', action="store", type=int )
  parser.add_argument('xlow', action="store", type=int )
  parser.add_argument('xhigh', action="store", type=int)
  parser.add_argument('ylow', action="store", type=int)
  parser.add_argument('yhigh', action="store", type=int)
  parser.add_argument('zlow', action="store", type=int)
  parser.add_argument('zhigh', action="store", type=int)
  parser.add_argument('--annid', action="store", type=int, help='Specify an identifier.  Server chooses otherwise.', default=0)
  parser.add_argument('--update', action='store_true')
  parser.add_argument('--dataonly', action='store_true')
  parser.add_argument('--preserve', action='store_true', help='Preserve exisiting annotations in the database.  Default is overwrite.')
  parser.add_argument('--exception', action='store_true', help='Store multiple nnotations at the same voxel in the database.  Default is overwrite.')

  result = parser.parse_args()

  anndata = np.ones ( [ result.zhigh-result.zlow, result.yhigh-result.ylow, result.xhigh-result.xlow ] )

  # Build a minimal hdf5 file
  # Create an in-memory HDF5 file
  tmpfile = tempfile.NamedTemporaryFile()
  h5fh = h5py.File ( tmpfile.name )

  h5fh.create_dataset ( "ANNOTATION_ID", (1,), np.uint32, data=result.annid )
  h5fh.create_dataset ( "RESOLUTION", (1,), np.uint32, data=result.resolution )
  h5fh.create_dataset ( "XYZOFFSET", (3,), np.uint32, data=[result.xlow,result.ylow,result.zlow] )
  h5fh.create_dataset ( "CUTOUT", anndata.shape, np.uint32, data=anndata )

  if result.preserve:  
    url = 'http://%s/annotate/%s/preserve/' % ( result.baseurl, result.token )
  elif result.exception:  
    url = 'http://%s/annotate/%s/exception/' % ( result.baseurl, result.token )
  else:
    url = 'http://%s/annotate/%s/' % ( result.baseurl, result.token )

  if result.update:
    url+='update/'

  if result.dataonly:
    url+='dataonly/'
  
  print url

  try:
    h5fh.flush()
    tmpfile.seek(0)
    req = urllib2.Request ( url, tmpfile.read())
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    print "Failed URL", url
    print "Error %s" % (e.read()) 
    sys.exit(0)

  the_page = response.read()
  print "Success with id %s" % the_page

if __name__ == "__main__":
  main()
