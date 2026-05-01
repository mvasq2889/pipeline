Troubleshooting
===============

Streaming Client
----------------

A Note About Subscriptions (and Kafka Commits)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ANTARES remembers which alerts you have or have not received. If you start
consuming alerts, stop and resume later, you will pick up where you left off.
Kafka provides the underlying functionality for ANTARES so, in Kafka-terms:
message offsets are automatically committed every 5 seconds.

"Could not locate SSL certificates"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connecting to ANTARES requires SSL certificates. The client will attempt to
find them automatically but there is a chance it may fail. If this happens,
you'll see an error message like "Could not locate SSL certificates".

You will need to manually locate your SSL certificates and pass their path
to the ANTARES client. Run the following command to see which directory
``openssl`` is configured to look for certificates in::

  openssl version -d

Look in the output directory for your certificates file--usually named
``certs.pem`` or ``ca-certificates.crt``. If you are using anaconda or miniconda, it
may be something like ``.../miniconda/ssl/cert.pem``.

If you are using the client as a command line tool, pass the option
``--ssl-ca-location /path/to/your/cert/file``. If you are using the client as a
library, pass the ``ssl_ca_location`` keyword argument to the ``Client`` constructor
(e.g. ``Client(..., ssl_ca_location="path/to/your/cert/file", ...)``).

Logging messages
~~~~~~~~~~~~~~~~

During normal operations, the client may lose its connection to ANTARES. When
this happens it will automatically attempt to reconnect. When this occurs, the
client wil continue to operate normally but you may see messages like::

  %3|1544735845.925|FAIL|rdkafka#consumer-1|
  [thrd:sasl_ssl://b0-pkc-epgnk.us-central1.gcp.confluent.cloud:9092/0]:
  sasl_ssl://b0-pkc-epgnk.us-central1.gcp.confluent.cloud:9092/0: Disconnected
  (after 600053ms in state UP)

Don't worry, this is normal!
