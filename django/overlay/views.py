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

import django.http

import numpy as np
from PIL import Image
import urllib2
import zlib

import cStringIO

import ocpcaproj
import ocpcarest

# Errors we are going to catch
from ocpcaerror import OCPCAError

from django.conf import settings

import logging
logger=logging.getLogger("ocp")

"""Merge two cutouts one from a data set and one from an annotation database"""

def overlayCutout (request, webargs):
  """Get both data and annotation cubes as npz"""
  alpha, token, cutout = webargs.split('/',2)
  alpha = float(alpha)

  # Get the project and dataset
  projdb = ocpcaproj.OCPCAProjectsDB()
  proj = projdb.loadProject ( token )
  
  # RBTODO assuming that the dataset name is the token.  Not the case anymore.
  dataurl = request.build_absolute_uri( '{}/ocpca/{}/{}'.format( proj.getDataURL(), proj.getDataset(), cutout ))
  #dataurl = request.build_absolute_uri( '%s%s/ocpca/%s/%s' % ( proj.getDataURL(),request.META.get('SCRIPT_NAME'), proj.getDataset(), cutout ))

  # RBTODO can't seen to get WSGIScriptAlias information from apache.  So 
  #  right now we have to hardwire.  Yuck.
  #
  #  dev server and production server urls.
  #
  annourl = request.build_absolute_uri( '{}/ocpca/{}/{}'.format( request.META.get('SCRIPT_NAME'), token, cutout ))
#  annourl = request.build_absolute_uri( '/ocpca/%s/%s' % ( token, cutout ))

  # Get data 
  try:
    f = urllib2.urlopen ( dataurl )
    # create the data image
    fobj = cStringIO.StringIO ( f.read() )
    dataimg = Image.open(fobj) 

  except:
    logger.error("Failed to fetch dataurl {}".format(dataurl))
    raise


  # Get annotations 
  try:
    f = urllib2.urlopen ( annourl )
    # create the annotation image
    fobj = cStringIO.StringIO ( f.read() )
    annoimg = Image.open(fobj) 

  except:
    logger.error("Failed to fetch annourl {}".format(annourl))
    raise

  try:
    # convert data image to RGBA
    dataimg = dataimg.convert("RGBA")
    annoimg = annoimg.convert("RGBA")
    # build the overlay
    
    compimg1 = Image.composite ( annoimg, dataimg, annoimg )
    compimg = Image.blend ( dataimg, compimg1, alpha )

    logger.warning("What up here.  {} {} {}".format(dataimg, annoimg, compimg))

  except Exception, e:
    logger.error ("Unknown error processing overlay images. Error={}".format(e))
    raise


  # Create blended image of the two
  return compimg


def imgAnnoOverlay (request, webargs):
  """Return overlayCutout as a png"""

  try:
    overlayimg = overlayCutout ( request, webargs )
  except Exception, e:
     raise
#    return django.http.HttpResponseNotFound(e)

  # write the merged image to a buffer
  fobj2 = cStringIO.StringIO ( )
  overlayimg.save ( fobj2, "PNG" )

  fobj2.seek(0)

  return django.http.HttpResponse(fobj2.read(), mimetype="image/png" )


