### OCP CATMAID service

* Instead of serving up CATMAID slices one by one, it loads a whole cube 
of data into memcache as slices and serves subsequent requests out of memcache.
* This requires the installation of memcache and python package pylibmc.
