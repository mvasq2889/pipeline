.. include:: ../global.rst.inc

Searching for Data
==================

The ``search`` module provides functionality for querying the ANTARES Database. The
search index is powered by ElasticSearch and we provide a handful of helpers for common
search operations.

The `antares-client` uses the ANTARES API to retrieve live data from its database.
It points by default to `https://api.antares.noirlab.edu/v1/`.

You can modify the API the client points to if you wish to access a different ANTARES
environment. This can be achieved by setting the ``ANTARES_API_BASE_URL`` variable. e.g.

.. code-block:: console

  export ANTARES_API_BASE_URL=https://api.antares.environment.url/v1/

To remove that variable (and return to the default) use:

.. code-block:: console

  unset ANTARES_API_BASE_URL

Lookup By ID
------------

You can lookup objects by their ANTARES IDs, LSST Dia Object IDs, or their ZTF Object IDs:

.. code:: python

   from antares_client.search import get_by_id, get_by_ztf_object_id, get_by_lsst_dia_object_id

   # Lookup by ANTARES ID
   locus = get_by_id("ANT2020j7wo4")

   # Lookup by LSST Dia Object ID
   locus = get_by_lsst_dia_object_id("169342393603063964")

   # Lookup by ZTF Object ID
   locus = get_by_ztf_object_id("ZTF20aafqubg")

Cone Searches
-------------

You can also find objects in particular locations of the sky:

.. code:: python

   from antares_client.search import cone_search
   from astropy.coordinates import Angle, SkyCoord

   center = SkyCoord("20h48m25.1805s 29d45m4.8361s")
   radius = Angle("1s")

   for locus in cone_search(center, radius):
       pass

Advanced Searches
-----------------

We also expose an API for writing queries directly against our ElasticSearch database.
These queries are complex but very powerful.

Let's say that we are interested in finding all loci with:

* Between 50 and 100 magnitude measurements
* Tagged as a nuclear transient

We represent this query in Python as follows:

.. code:: python

   query = {
       "query": {
           "bool": {
               "filter": [
                   {
                       "range": {
                           "properties.num_mag_values": {
                               "gte": 50,
                               "lte": 100,
                           } 
                       }
                   },
                   {
                        "term": {
                            "tags": "nuclear_transient"
                        }
                   }
                ]
           }
       }
   }

And can search through the ANTARES database for matching objects:

.. code:: python

   from antares_client.search import search
   first_result = next(search(query))

The return value of the ``search`` function is an iterator over loci in the result set.
This means that the result set is not immediately available in memory unless you did
something like ``result_set = list(search(query))``. Because result sets can be so large,
we recommend against doing so. Prefer, instead, operations on the iterable like:

.. code:: python

   for locus in search(query):
       do_something(locus)

Query Helpers
-------------

We plan to provide a number of tools to simplify writing queries in the future. In the meantime,
you can use the Python ``elasticsearch_dsl`` library to remove some of the boilerplate associated
with structuring ElasticSearch queries.

If you've run ``pip install elasticsearch-dsl``, you could also accomplish the previous example with:

.. code:: python

   from antares_client.search import search
   from elasticsearch_dsl import Search

   query = (
       Search()
       .filter("range", **{"properties.num_mag_values": {"gte": 50, "lte": 100}})
       .filter("term", tags="nuclear_transient")
       .to_dict()
   )
   first_result = next(search(query))

Query Syntax
------------

Queries can have a complex and deep structure. Most queries will be nested
within a `bool` structure, this allows multiple conditions to exist together.
Let's look at the conditional structures:

Must
~~~~

All documents must match the clause in order to be returned. Think of this as an
analog to *AND*. Notice that you can have multiple conditions, these are placed
within a list using square brackets (`[]`).

.. code:: json

   {
     "query":{
       "bool":{
         "must":[
            {
              "match":{
                  "properties.anomaly": "-1"
                }
            },
            {
              "range":{
                "properties.num_mag_values":{
                  "gte": 10
                }
              }
            }
         ]
       }
     }
   }
              
Should
~~~~~~
                
Any documents that match one or more criteria are returned. `should` is not
exclusive, think of this as the analog to *OR*. These can also be placed
in a list.

.. code:: json

   {
     "query":{
       "bool":{
         "should":[
            {
              "range":{
                "properties.anomaly_score":{
                  "gte": "0.5"
                }
              }
            },
            {
              "range":{
                "properties.brightest_alert_magnitude":{
                  "lte": "14.99"
                }
              }
            }
         ]
       }
     }
   }
              
Must Not
~~~~~~~~

`must_not` is the logical *NOT* operator.

.. code:: json

   {
     "query":{
       "bool":{
         "must_not":[
            {
              "match":{
                "properties.anomaly": "1"
              }
            },
            {
              "match":{
                "properties.anomaly": "-1"
              }
            }
         ]
       }
     }
   }
              
Ranges
~~~~~~
                
Ranges can have `gt`, `lt`, `gte`, `lte` (greater-than, less-than,
greater-or-equal, less-or-equal respectively) conditions.

.. code:: json

   {
     "query":{
       "bool":{
         "should":[
            {
              "range":{
                "properties.newest_alert_magnitude":{
                  "lt": "17.01",
                  "gte": "16.01"
                }
              }
            },
            {
              "range":{
                "properties.brightest_alert_magnitude":{
                  "lte": "14.99"
                }
              }
            }
         ]
       }
     }
   }

Set Membership
~~~~~~~~~~~~~~
               
You can search for alerts that have properties in a given set of values with
the `terms` property.

.. code:: json

   {
     "query": {
       "bool": {
         "filter": {
           "terms": {
             "locus_id": [
               "ANT2020a17",
               "ANT2020a65",
               "ANT2020a67",
               "ANT2020a41",
               "ANT2020a43",
               "ANT2020a26",
               "ANT2020a19",
               "ANT2020a37"
             ]
           }
         }
       }
     }
   }

Compound Queries
~~~~~~~~~~~~~~~~

You can combine these different conditional clauses to write advanced
queries. For example:

.. code:: json

   {
     "query":{
       "bool":{
         "must_not":[
            {
              "match":{
                  "properties.anomaly": "1"
                }
            },
            {
              "range":{
                "dec":{
                  "gte":20.23,
                  "lte":28.00
                }
              }
            }
         ],
         "must":[
           {
             "range":{
               "newest_alert_observation_time":{
                 "gte": 58000,
                 "lt": 58001
               }
             }
           }
         ],
         "should":[
            {
              "range":{
                "ra":{
                  "lte": 66.13
                }
              }
            }
         ]
       }
     }
   }

Get available tags
------------------

You can lookup available tags for searches:

.. code:: python

   from antares_client.search import get_available_tags

   tags = get_available_tags()

Get latest gravitational wave notices
-------------------------------------

You can lookup gravitational wave notices by their gracedb id:

.. code:: python

   from antares_client.search import get_latest_grav_wave_notices

   # Lookup by GraceDB ID 
   gravitational_wave_notice = get_latest_grav_wave_notices("S231103aa")

Get a specific gravitational wave notice
----------------------------------------

You can lookup a specific gravitational wave notice by its gracedb id and datetime:

.. code:: python

   from antares_client.search import get_grav_wave_notices
   import datetime

   # Lookup by GraceDB ID and datetime
   gravitational_wave_notice = get_grav_wave_notices("S231103aa", datetime.datetime(2023, 11, 3, 18, 58, 2))

Get multiple gravitational wave notices by their ids
----------------------------------------------------

You can lookup multiple gravitational wave notices at once by their gracedb ids (instead of retrieving one by one):

.. code:: python

   from antares_client.search import get_multiple_grav_wave_notices

   gravitational_wave_notices = get_multiple_grav_wave_notices(["S231004f","S231004q"])


Get a sample of catalog data
----------------------------

You can retrieve a sample of catalogs data of size n:

.. code:: python

   from antares_client.search import get_catalog_samples

   # Retrieve 5 rows from each catalog available
   catalog_data = get_catalog_samples(5)

Search catalog data
-------------------

You can get the results of catalog cross-matching:

.. code:: python

   from antares_client.search import catalog_search

   # Retrieve all catalog crossmatches for a position
   catalog_data = catalog_search(ra=316.7859, dec=13.1324)

Get thumbnails of an alert
--------------------------

You can retrieve the alert thumbnails by its id:

.. code:: python

   from antares_client.search import get_thumbnails

   # Get all thumbnails for an LSST alert
   lsst_thumbnails = get_thumbnails("lsst:169342393603063964")

   # Get all thumbnails for a ZTF candidate
   ztf_thumbnails = get_thumbnails("ztf_candidate:2552120390115015005")
