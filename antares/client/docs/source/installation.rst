.. include:: global.rst.inc

.. _installation:

Installation and Setup
======================

The ANTARES client supports Python versions 3.7 and up.

.. code:: bash

   $ pip install antares-client

To install with confluent_kafka to use the StreamingClient.

.. code:: bash
   $ pip install "antares-client[subscriptions]"

Verify the client installed correctly:

.. code:: bash

   $ antares --version
   antares, version 1.11.0

.. note::
   Python 3.10 Prerequisites

   :code:`librdkafka` is required to install antares-client with
   python 3.10 when installing the optional subscriptions packages

   Mac: :code:`brew install librdkafka`

   Ubuntu: :code:`apt-get install librdkafka-dev`

Installing for Development
--------------------------

If you plan on contributing to the development of the ANTARES client or if you
want to run the latest (unreleased) version of the library, you may want to
install in development mode.

.. code:: bash

   $ git clone https://gitlab.com/nsf-noirlab/csdc/antares/client
   $ cd client
   $ python setup.py develop
   $ antares --version
   antares, version v1.1.0

Obtaining Credentials
---------------------

You'll need to contact the ANTARES team to request API credentials if you'd
like to access the real-time alert stream.

These credentials are different than your sign-in credentials for the `ANTARES
Portal`_. We typically grant only one set of credentials per institution. Please do
not share these credentials with others, and we request that you operate only one
active streaming client per set of credentials, except with permission.

We reserve the right to monitor usage and revoke access at any time.
