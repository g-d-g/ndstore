import urllib2
import cStringIO
import sys
import os
import tempfile
import h5py
import random 
import csv
import numpy as np
import zlib
import pytest

EM_BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".." ))
EM_EMCA_PATH = os.path.join(EM_BASE_PATH, "emca" )
sys.path += [ EM_EMCA_PATH ]

#SITE_HOST = 'openconnecto.me'
SITE_HOST = 'localhost:8000'
#SITE_HOST = 'localhost'

import emcaproj

# Module level setup/teardown
def setup_module(module):
  pass
def teardown_module(module):
  pass


class ReadParms:
  baseurl = ""
  token = ""
  resolution = None
  annids = None
  voxels = False
  cutout = None
  tightcutout = False
  boundingbox = False

def readAnno ( params ):
  """Modified version of annoread that takes the following dictionary
     params -- with fields 
       baseurl
       token 
       resolution = number 
       annids = 1,2,3,4,5
       voxels = None or True
       cutout = form 0/100,200/100,200/1,2 or None
       tightcutout = None of True
   """

  if params.voxels:
    url = "http://%s/emca/%s/%s/voxels/%s/" % (params.baseurl,params.token,params.annids, params.resolution)
  elif params.cutout != None:
    url = "http://%s/emca/%s/%s/cutout/%s/" % (params.baseurl,params.token,params.annids, params.cutout)
  elif params.tightcutout: 
    url = "http://%s/emca/%s/%s/cutout/%s/" % (params.baseurl,params.token,params.annids, params.resolution)
  elif params.boundingbox: 
    url = "http://%s/emca/%s/%s/boundingbox/%s/" % (params.baseurl,params.token,params.annids, params.resolution)
  else:
    url = "http://%s/emca/%s/%s/" % (params.baseurl,params.token,params.annids)

  # Get annotation in question
  f = urllib2.urlopen ( url )

  # Read into a temporary file
  tmpfile = tempfile.NamedTemporaryFile ( )
  tmpfile.write ( f.read() )
  tmpfile.tell()
  h5f = h5py.File ( tmpfile.name, driver='core', backing_store=False )

  return h5f


class H5Anno:

  def __init__(self):

    # Create an in-memory HDF5 file
    self.tmpfile = tempfile.NamedTemporaryFile()
    self.h5fh = h5py.File ( self.tmpfile.name )

  def __del__(self):
    self.tmpfile.close()


  def addAnno ( self, annotype, annoid, kv=None ):
    """Add an annotation to the file."""

    # Create the top level annotation id namespace
    idgrp = self.h5fh.create_group ( str(annoid) )

    # Annotation type
    idgrp.create_dataset ( "ANNOTATION_TYPE", (1,), np.uint32, data=annotype )

    # Create a metadata group
    mdgrp = idgrp.create_group ( "METADATA" )

    # now lets add a bunch of random values for the specific annotation type
    ann_status = random.randint(0,4)
    ann_confidence = random.random()
    ann_author = 'randal'

    # Set Annotation specific metadata
    mdgrp.create_dataset ( "STATUS", (1,), np.uint32, data=ann_status )
    mdgrp.create_dataset ( "CONFIDENCE", (1,), np.float, data=ann_confidence )
    mdgrp.create_dataset ( "AUTHOR", (1,), dtype=h5py.special_dtype(vlen=str), data=ann_author )

    kvpairs={}
    if kv!= None:
      [ k, sym, v ] = kv.partition(':')
      kvpairs[k]=v

      # Turn our dictionary into a csv file
      fstring = cStringIO.StringIO()
      csvw = csv.writer(fstring, delimiter=',')
      csvw.writerows([r for r in kvpairs.iteritems()])

      # User-defined metadata
      mdgrp.create_dataset ( "KVPAIRS", (1,), dtype=h5py.special_dtype(vlen=str), data=fstring.getvalue())

    # Synapse:
    if annotype == 2:

      syn_weight = random.random()*1000.0
      syn_synapse_type = random.randint(1,9)
      syn_seeds = [ random.randint(1,1000) for x in range(5) ]

      syn_segments = [ [random.randint(1,1000),random.randint(1,1000)] for x in range(4) ]

      mdgrp.create_dataset ( "WEIGHT", (1,), np.float, data=syn_weight )
      mdgrp.create_dataset ( "SYNAPSE_TYPE", (1,), np.uint32, data=syn_synapse_type )
      mdgrp.create_dataset ( "SEEDS", (len(syn_seeds),), np.uint32, data=syn_seeds )
      mdgrp.create_dataset ( "SEGMENTS", (len(syn_segments),2), np.uint32, data=syn_segments)

    # Seed
    elif annotype == 3:

      seed_parent = random.randint(1,1000)
      seed_position = [ random.randint(1,10000) for x in range(3) ]
      seed_cubelocation = random.randint(1,9)
      seed_source = random.randint(1,1000)

      mdgrp.create_dataset ( "PARENT", (1,), np.uint32, data=seed_parent )
      mdgrp.create_dataset ( "CUBE_LOCATION", (1,), np.uint32, data=seed_cubelocation )
      mdgrp.create_dataset ( "SOURCE", (1,), np.uint32, data=seed_source )    
      mdgrp.create_dataset ( "POSITION", (3,), np.uint32, data=seed_position )

    # Segment
    elif annotype == 4:
       
      seg_parentseed = random.randint(1,100000)
      seg_segmentclass = random.randint(1,9)
      seg_neuron = random.randint(1,100000)
      seg_synapses = [ random.randint(1,100000) for x in range(5) ]
      seg_organelles = [ random.randint(1,100000) for x in range(5) ]

      mdgrp.create_dataset ( "SEGMENTCLASS", (1,), np.uint32, data=seg_segmentclass )
      mdgrp.create_dataset ( "PARENTSEED", (1,), np.uint32, data=seg_parentseed )
      mdgrp.create_dataset ( "NEURON", (1,), np.uint32, data=seg_neuron )
      mdgrp.create_dataset ( "SYNAPSES", (len(seg_synapses),), np.uint32, seg_synapses )
      mdgrp.create_dataset ( "ORGANELLES", (len(seg_organelles),), np.uint32, seg_organelles )

    # Neuron
    elif annotype == 5:

      neuron_segments = [ random.randint(1,1000) for x in range(10) ]
      mdgrp.create_dataset ( "SEGMENTS", (len(neuron_segments),), np.uint32, neuron_segments )

    # Organelle
    elif annotype == 6:

      org_parentseed = random.randint(1,100000)
      org_organelleclass = random.randint(1,9)
      org_seeds = [ random.randint(1,100000) for x in range(5) ]
      org_centroid = [ random.randint(1,10000) for x in range(3) ]

      mdgrp.create_dataset ( "ORGANELLECLASS", (1,), np.uint32, data=org_organelleclass )
      mdgrp.create_dataset ( "PARENTSEED", (1,), np.uint32, data=org_parentseed )
      mdgrp.create_dataset ( "SEEDS", (len(org_seeds),), np.uint32, org_seeds )
      mdgrp.create_dataset ( "CENTROID", (3,), np.uint32, data=org_centroid )

  def getFileObject(self):
    """Return a file object to be posted to a URL"""
    self.h5fh.flush()
    self.tmpfile.seek(0)
    # return and file object to be posted
    return self.tmpfile


  def addCutout (self, annid, cutout):
    """Add a cube of data to the HDF5 file"""

    [ resstr, xstr, ystr, zstr ] = cutout.split('/')
    ( xlowstr, xhighstr ) = xstr.split(',')
    ( ylowstr, yhighstr ) = ystr.split(',')
    ( zlowstr, zhighstr ) = zstr.split(',')

    resolution = int(resstr)
    xlow = int(xlowstr)
    xhigh = int(xhighstr)
    ylow = int(ylowstr)
    yhigh = int(yhighstr)
    zlow = int(zlowstr)
    zhigh = int(zhighstr)

    idgrp = self.h5fh[str(annid)]

    anndata = np.ones ( [ zhigh-zlow, yhigh-ylow, xhigh-xlow ] )
    idgrp.create_dataset ( "RESOLUTION", (1,), np.uint32, data=resolution )
    idgrp.create_dataset ( "XYZOFFSET", (3,), np.uint32, data=[xlow,ylow,zlow] )
    idgrp.create_dataset ( "CUTOUT", anndata.shape, np.uint32, data=anndata )


  def addVoxels(self, annid, cutout):
    """Add a cube of data to the HDF5 file as a list of voxels"""

    [ resstr, xstr, ystr, zstr ] = cutout.split('/')
    ( xlowstr, xhighstr ) = xstr.split(',')
    ( ylowstr, yhighstr ) = ystr.split(',')
    ( zlowstr, zhighstr ) = zstr.split(',')

    resolution = int(resstr)
    xlow = int(xlowstr)
    xhigh = int(xhighstr)
    ylow = int(ylowstr)
    yhigh = int(yhighstr)
    zlow = int(zlowstr)
    zhigh = int(zhighstr)

    voxlist=[]

    for k in range (zlow,zhigh):
      for j in range (ylow,yhigh):
        for i in range (xlow,xhigh):
          voxlist.append ( [ i,j,k ] )

    idgrp = self.h5fh[str(annid)]

    # make annid 0 if it's not an integer
    if not isinstance(annid,int):
      annid = 0

    idgrp.create_dataset ( "ANNOTATION_ID", (1,), np.uint32, data=annid )
    idgrp.create_dataset ( "RESOLUTION", (1,), np.uint32, data=resolution )
    idgrp.create_dataset ( "VOXELS", (len(voxlist),3), np.uint32, data=voxlist )



class WriteParms:
  """Arguments to write anno"""
  token = ""
  baseurl = ""
  numobjects = 1
  annid = 0
  voxels = False
  cutout = None
  anntype = 1
  update = False
  dataonly = False 
  preserve = False
  exception = False
  overwrite = False
  shave = False

def writeAnno ( params ): 
  """Write an annotation derived from annowrite"""

  h5ann = H5Anno()
  for i in range(params.numobjects):
    # either anonymous annotations ids
    if params.annid==0:
      annid = 'noid.'+str(i)
    # or a sequence starting from params.annid
    else:
      annid=params.annid+i

    # if mutliple objects and no type, insert random object types
    if params.anntype==1 and params.numobjects > 1 and not params.voxels and not params.cutout:
      anntype = random.randint(1,6)
    else:
      anntype = params.anntype

    # don't test kvpairs, that's part of test_ramon
    h5ann.addAnno ( anntype, annid, None )

    if params.cutout:
      if params.voxels:
        h5ann.addVoxels ( annid, params.cutout )
      else:
        h5ann.addCutout ( annid, params.cutout )

  # get the file handle
  fileobj = h5ann.getFileObject()

  # Build the put URL
  if params.update:
    url = "http://%s/emca/%s/update/" % ( params.baseurl, params.token)
  elif params.dataonly:
    url = "http://%s/emca/%s/dataonly/" % ( params.baseurl, params.token)
  else:
    url = "http://%s/emca/%s/" % ( params.baseurl, params.token)

  if params.preserve:  
    url += 'preserve/'
  elif params.exception:  
    url += 'exception/'
  elif params.overwrite:  
    url += 'overwrite/'
  elif params.shave:  
    url += 'reduce/'

  try:
    req = urllib2.Request ( url, fileobj.read()) 
    response = urllib2.urlopen(req)
  except urllib2.URLError, e:
    assert 0

  return response.read()


def countVoxels ( annid, h5 ):
  """Count the number of voxels in an HDF5 file for an annotation id"""

  keys = h5.keys()
  for k in keys:
    if int(k) == int(annid):
      idgrp = h5.get(k)
      if idgrp.get('VOXELS'):
        return len(idgrp['VOXELS'][:])
      elif idgrp.get('CUTOUT') and idgrp.get('XYZOFFSET'):
        return len(np.nonzero(np.array(idgrp['CUTOUT'][:,:,:]))[0])
  return 0

   


class TestRW:

# Per method setup/teardown
#  def setup_method(self,method):
#    pass
#  def teardown_method(self,method):
#    pass

  def setup_class(self):
    """Create the unittest database"""
    
    self.pd = emcaproj.EMCAProjectsDB()
    self.pd.newEMCAProj ( 'unittest_rw', 'test', 'localhost', 'unittest_rw', 2, 'kasthuri11', None, False, True )

  def teardown_class (self):
    """Destroy the unittest database"""
    self.pd.deleteEMCADB ('unittest_rw')

  def test_rw(self):
    """A battery of read and writes"""

    rp = ReadParms()
    wp = WriteParms()

    # variables for all tests
    # read
    rp.token = "unittest_rw"
    rp.baseurl = SITE_HOST
    rp.resolution = 0

    # write
    wp.token = "unittest_rw"
    wp.baseurl = SITE_HOST
    wp.resolution = 0

    # upload voxels (anonymous id)
    wp.numobjects = 1
    wp.voxels = True
    wp.cutout = "0/100,200/100,200/1,2"

    # Write one object as voxels
    retval = writeAnno(wp) 
    assert retval >= 1

    # Read it as voxels and as a cutout
    rp.resolution = 0
    rp.annids = retval
    rp.voxels = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 100*100*1

    rp.annids = retval
    rp.voxels = False
    rp.tightcutout = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 100*100*1

    #TODO read it as a range with cutout

    # Write one object as a cutout
    wp.voxels=False
    retval = writeAnno ( wp ) 
    assert retval >= 1

    # Read it as voxels and as a cutout
    rp.annids = retval
    rp.voxels = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 100*100*1

    rp.annids = retval
    rp.voxels = False
    rp.tightcutout = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 100*100*1

  def test_update(self):
    """Updates"""

    rp = ReadParms()
    wp = WriteParms()

    # variables for all tests
    # read
    rp.token = "unittest_rw"
    rp.baseurl = SITE_HOST
    rp.resolution = 0

    # write
    wp.token = "unittest_rw"
    wp.baseurl = SITE_HOST
    wp.resolution = 0

    # upload voxels (anonymous id)
    wp.numobjects = 1
    wp.voxels = True
    wp.cutout = "0/500,550/500,550/1849,1850"

    # Write one object as voxels
    retval = writeAnno(wp) 
    assert int(retval) >= 1

    # update the object
    wp.annid = int(retval)
    wp.update = True
    wp.cutout = "0/550,600/550,600/1849,1850"
    retval = writeAnno(wp) 

    # Check that the combination of write + update sums
    rp.resolution = 0
    rp.annids = int(retval)
    rp.voxels = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 2*50*50*1

    # update the object as dense
    wp.voxels = False
    wp.cutout = "0/600,650/600,650/1849,1850"
    writeAnno(wp) 

    # Check that the combination of write + update sums
    rp.voxels = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 3*50*50*1

    # shave the annotation
    wp.cutout = "0/500,550/500,550/1849,1850"
    wp.update = False
    wp.shave = True
    wp.voxels = True
    writeAnno(wp) 

    # Check that the shave worked
    rp.voxels = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 2*50*50*1

    # shave half of the remaining annotation as dense
    wp.cutout = "0/550,600/550,600/1849,1850"
    wp.shave = True
    wp.voxels = False
    writeAnno(wp) 

    # Check that the shave worked
    rp.voxels = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 50*50*1 

    # And delete
    import httplib
    conn = httplib.HTTPConnection ( "%s" % ( rp.baseurl ))
    conn.request ( 'DELETE', '/emca/%s/%s/' % ( rp.token, rp.annids ))
    resp = conn.getresponse()
    content=resp.read()
    assert content == "Success"

    # Verify that we can't read it anymore
    with pytest.raises(urllib2.HTTPError): 
      h5r = readAnno(rp)


  def test_dataonly(self):
    """Data only option."""

    rp = ReadParms()
    wp = WriteParms()

    # read
    rp.token = "unittest_rw"
<<<<<<< HEAD
    rp.baseurl = "openconnecto.me"
    # write
    wp.token = "unittest_rw"
    wp.baseurl = "openconnecto.me"
=======
    rp.baseurl = SITE_HOST
    rp.resolution = 0
   
    # write
    wp.token = "unittest_rw"
    wp.baseurl = SITE_HOST
    wp.resolution = 0
>>>>>>> 3a5784160c69fdb21173ab82c2eb1577eae5a143

    # Create an annotation
    wp.numobjects = 1
    retval = writeAnno(wp) 
    assert int(retval) >= 1

    # Add data to it
    wp.annid=int(retval)
    wp.voxels = True
    wp.cutout = "0/500,550/500,550/1000,1002"
    wp.dataonly = True
    writeAnno(wp) 

    # Add data to it
    wp.annid=int(retval)
    wp.voxels = False
    wp.cutout = "0/600,650/600,650/1000,1002"
    wp.dataonly = True
    writeAnno(wp) 

    # Check that the combination of write + update sums
    rp.annids=int(retval)
    rp.voxels = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 2*50*50*2

  def test_batch(self):
    """Batch interface"""
    pass

  def test_npz(self):
    """npz upload/download"""

    rp = ReadParms()
    wp = WriteParms()

    # read
    rp.token = "unittest_rw"
<<<<<<< HEAD
    rp.baseurl = "openconnecto.me"
    # write
    wp.token = "unittest_rw"
    wp.baseurl = "openconnecto.me"
=======
    rp.baseurl = SITE_HOST
    rp.resolution = 0

    # write
    wp.token = "unittest_rw"
    wp.baseurl = SITE_HOST
    wp.resolution = 0
>>>>>>> 3a5784160c69fdb21173ab82c2eb1577eae5a143

    # Create an annotation
    wp.numobjects = 1
    retval = writeAnno(wp) 
    assert int(retval) >= 1

    wp.annid = int(retval)
    wp.resolution = 0
    
    voxlist=[]

    # upload an npz voxels list
    for k in range (100,102):
      for j in range (1000,1050):
        for i in range (1000,1050):
          voxlist.append ( [ i,j,k ] )

    url = 'http://%s/emca/%s/npvoxels/%s/%s/' % ( wp.baseurl, wp.token, int(retval), wp.resolution)

    # Encode the voxelist an pickle
    fileobj = cStringIO.StringIO ()
    np.save ( fileobj, voxlist )

    # Build the post request
    req = urllib2.Request(url, fileobj.getvalue())
    response = urllib2.urlopen(req)

    # Check that the combination of write + update sums
    rp.annids=int(retval)
    rp.voxels = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 50*50*2

    # upload an npz dense
    annodata = np.zeros( [ 2, 50, 50 ] )
    annodata = annodata + int(retval)

    url = 'http://%s/emca/%s/npdense/%s/%s,%s/%s,%s/%s,%s/' % ( wp.baseurl, wp.token, wp.resolution, 200, 250, 200, 250, 200, 202 )

    # Encode the voxelist as a pickle
    fileobj = cStringIO.StringIO ()
    np.save ( fileobj, annodata )
    cdz = zlib.compress (fileobj.getvalue())

    # Build the post request
    req = urllib2.Request(url, cdz)
    response = urllib2.urlopen(req)

    # Check that the combination of write + update sums
    rp.annids=int(retval)
    rp.voxels = True
    h5r = readAnno(rp)
    assert countVoxels ( retval, h5r ) == 2*50*50*2

