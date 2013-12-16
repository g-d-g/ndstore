import numpy as np
from PIL import Image
import urllib2
import zlib
import StringIO

#
#  makePNGs
#
#  First RESTful client program.
#  Download a cube and write out PNGs.
#

#
# Extract data from the cube and write out PNG files.
#
def cubeToPNGs ( nparray, prefix ):
  """Convert a numpy array into PNG files"""  

  # Note the data order is z then y then x
  zdim,ydim,xdim = nparray.shape

  # One file per xz plane
  for j in range(ydim):
    outimage = Image.frombuffer ( 'L', (xdim,zdim), nparray[:,j,:].flatten(), 'raw', 'L', 0, 1 ) 
    outimage.save ( prefix + str(j) + ".png", "PNG" )
    t = nparray[:,j,:]
    print (np.unique(t))


# Get cube in question
try:

#  url = "http://localhost/emca/bock11/npz/7/0,1088/0,960/2917,3013/neariso/"
#  url = "http://rio.cs.jhu.edu/ocp/ocpca/kasthuri11/npz/7/0,192/0,256/1,142/neariso/"
#  url = "http://openconnecto.me/ocp/ocpca/kasthuri11/npz/5/100,300/200,448/1,400/neariso/"
#  url = "http://openconnecto.me/ocp/ocpca/kasthuri11/npz/5/100,700/200,500/1,500/neariso/"
#  url = "http://openconnecto.me/ocp/ocpca/bock11/npz/7/0,1088/0,960/2917,3013/neariso/"
#  url = "http://openconnecto.me/emca/bock11/npz/4/4000,5000/4000,4050/2917,3413/neariso/"
  url = "http://localhost/ocp/ocpca/kasthuri11/npz/7/0,192/0,256/1,143/neariso/"
  f = urllib2.urlopen ( url )
except urllib2.URLError, e:
  print "Failed to open url ", url, e
  assert 0

zdata = f.read ()

# get the data out of the compressed blob
pagestr = zlib.decompress ( zdata[:] )
pagefobj = StringIO.StringIO ( pagestr )
cube = np.load ( pagefobj )

# Write out the cube as files
cubeToPNGs ( cube, "/tmp/npz" )
