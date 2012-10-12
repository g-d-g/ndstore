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

  # One file per xy plane
  for k in range(zdim):
    outimage = Image.frombuffer ( 'L', (xdim,ydim), nparray[k,:,:].flatten(), 'raw', 'L', 0, 1 ) 
    outimage.save ( prefix + str(k) + ".png", "PNG" )


# Get cube in question
try:

  url = "http://localhost:8000/emca/hayworth5nm/npz/2/0,2000/0,2000/0,10/"
  f = urllib2.urlopen ( url )
except urllib2.URLError:
  print "Failed to open url ", url
  assert 0

zdata = f.read ()

# get the data out of the compressed blob
pagestr = zlib.decompress ( zdata[:] )
pagefobj = StringIO.StringIO ( pagestr )
cube = np.load ( pagefobj )

# Write out the cube as files
cubeToPNGs ( cube, "/tmp/npz" )
