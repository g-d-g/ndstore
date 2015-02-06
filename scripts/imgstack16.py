# Copyright 2014 Open Connectome Project (http://openconnecto.me)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys
import os
import numpy as np
import urllib, urllib2
import cStringIO
from PIL import Image
import zlib
import MySQLdb

sys.path += [os.path.abspath('../django')]
import OCP.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'OCP.settings'
from django.conf import settings

import ocplib
import ocpcaproj
import ocpcadb
import zindex

"""Construct an image hierarchy up from a given resolution"""

class ImgStack:
  """Stack of images."""

  def __init__(self, token):
    """Load the database and project"""

    projdb = ocpcaproj.OCPCAProjectsDB()
    self.proj = projdb.loadProject ( token )

    # Bind the annotation database
    self.imgDB = ocpcadb.OCPCADB ( self.proj )


  def buildStack ( self, startlevel ):
    """Build the hierarchy of images"""

    for  l in range ( startlevel, len(self.proj.datasetcfg.resolutions) ):

      # Get the source database sizes
      [ximagesz, yimagesz] = self.proj.datasetcfg.imagesz [ l ]
      [xcubedim, ycubedim, zcubedim] = self.proj.datasetcfg.cubedim [ l ]

      biggercubedim = [xcubedim*2,ycubedim*2,zcubedim]

      # Get the slices
      [ startslice, endslice ] = self.proj.datasetcfg.slicerange
      slices = endslice - startslice + 1

      # Set the limits for iteration on the number of cubes in each dimension
      # RBTODO These limits may be wrong for even (see channelingest.py)
      xlimit = ximagesz / xcubedim
      ylimit = yimagesz / ycubedim
      #  Round up the zlimit to the next larger
      zlimit = (((slices-1)/zcubedim+1)*zcubedim)/zcubedim 

      cursor = self.imgDB.conn.cursor()

      for z in range(zlimit):
        for y in range(ylimit):
          self.imgDB.conn.commit()
          for x in range(xlimit):

            # cutout the data at the -1 resolution
            olddata = self.imgDB.cutout ( [ x*2*xcubedim, y*2*ycubedim, z*zcubedim ], biggercubedim, l-1 ).data
            # target array for the new data (z,y,x) order
            newdata = np.zeros([zcubedim,ycubedim,xcubedim], dtype=np.uint16)

            for sl in range(zcubedim):

              # Convert each slice to an image
              slimage = Image.frombuffer ( 'I;16', (xcubedim*2,ycubedim*2), olddata[sl,:,:].flatten(), 'raw', 'I;16', 0, 1 )

              # Resize the image
              newimage = slimage.resize ( [xcubedim,ycubedim] )
              
              # Put to a new cube
              newdata[sl,:,:] = np.asarray ( newimage )

              # Compress the data
              outfobj = cStringIO.StringIO ()
              np.save ( outfobj, newdata )
              zdataout = zlib.compress (outfobj.getvalue())
              outfobj.close()

            key = zindex.XYZMorton ( [x,y,z] )
            
            # put in the database
            sql = "INSERT INTO res" + str(l) + "(zindex, cube) VALUES (%s, %s)"
            print sql % (key,"x,y,z=%s,%s,%s"%(x,y,z))
            try:
              cursor.execute ( sql, (key,zdataout))
            except MySQLdb.Error, e:
              print "Failed insert %d: %s. sql=%s" % (e.args[0], e.args[1], sql)

      self.imgDB.conn.commit()

def main():

  parser = argparse.ArgumentParser(description='Build an image stack')
  parser.add_argument('token', action="store", help='Token for the project.')
  parser.add_argument('resolution', action="store", type=int, help='Start (highest) resolution to build')
  
  result = parser.parse_args()

  # Create the annotation stack
  imgstack = ImgStack ( result.token )

  # Iterate over the database creating the hierarchy
  imgstack.buildStack ( result.resolution )
  


if __name__ == "__main__":
  main()

