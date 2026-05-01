.. _tutorial-streaming:

Streaming Alerts
================

ANTARES distributes alerts over topic-specific streams--like the ``extragalactic_staging``
or ``nuclear_transient_staging`` streams, contact the team to get the full stream list.
The ANTARES client provides a high-level
interface for receiving alerts from these streams with the ``StreamingClient`` object.
We will highlight a few of the most useful ways you can use the object here, but have
a look at the :ref:`api` for the full documentation. 

To import and instantiate the ``StreamingClient``:

.. code:: python

   from antares_client import StreamingClient
   client = StreamingClient(
       topics=["extragalactic_staging", "nuclear_transient_staging"],
       api_key="********************",
       api_secret="********************",
   )

The ``poll`` method can be used to retrieve an alert. It returns a
``(topic, locus)`` tuple where ``topic`` is a string (in this example either
``"extragalactic_staging"`` or ``"nuclear_transient_staging"``) and ``locus`` is a ``Locus`` instance
that contains the history of observations at the alert site. By default, this method will block
indefinitely, waiting for an alert. If you pass an argument to the ``timeout``
keyword, the method will return ``(None, None)`` after ``timeout`` seconds have
elapsed:

.. code:: python

   topic, locus = client.poll(timeout=10)
   if locus:
       print("received an alert")
   else:
       print("waited 10 seconds but didn't get an alert")

Often you'll want to consume alerts in real-time from ANTARES. This pattern is
common enough that ``StreamingClient`` objects provide the ``iter`` method:

.. code:: python

  # This...
  for topic, locus in client.iter():
      print("received {} on {}".format(locus, topic))

  # Is equivalent to...
  while True:
      topic, locus = client.poll()
      print("received {} on {}".format(locus, topic))

Note, though, that you're unable to control timeout behavior with the former
approach.

You should also close your connection to the client and you can do that explicitly
with the ``close`` method. The ``Client`` also wraps this behavior in a context
manager so:

.. code:: python

   # This...
   with StreamingClient(topics, **config) as client:
       for topic, locus in client.iter():
           print("received {} on {}".format(locus, topic))

   # Is equivalent to...
   client = StreamingClient(topics, **config)
   try:
       for topic, locus in client.iter():
           print("received {} on {}".format(locus, topic))
   finally:
       client.close()

Example
-------

.. code:: python

   """
   Use this script as a starting point for streaming alerts from ANTARES.

   Author: YOUR_NAME

   """

   from antares_client import StreamingClient

   TOPICS = ["extragalactic_staging", "nuclear_transient_staging"]
   CONFIG = {
       "api_key": "YOUR_API_KEY",
       "api_secret": "YOUR_API_SECRET",
   }


   def process_alert(topic, locus):
       """Put your code here!"""
       pass

   
   def main():
      with StreamingClient(TOPICS, **CONFIG) as client:
          for topic, locus in client.iter():
              process_alert(topic, locus)
   
   
   if __name__ == "__main__":
       main()
