Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`__

__ https://keepachangelog.com/en/1.0.0/

Unreleased
----------

1.14.0
----------

Added
~~~~~~~
- The `get_by_lsst_ss_object_id` method to retrieve lsst alerts based on their solar system object_id.

Changed
~~~~~~~
- The `confluent_kafka` package is no longer pinned to 1.7.0, allowing the use of more recent releases.

1.13.0
----------

Added
~~~~~~~
- The `get_by_lsst_dia_object_id` method to retrieve lsst alerts based on their object_id.

1.12.0
----------

Added
~~~~~~~
- The `ANTARES_API_BASE_URL` and `API_TIMEOUT` environment variables can be used to update the client configuration.

1.11.1
----------

Fixed
~~~~~
- Fixed `KafkaStreamingClient` to skip loci messages that are incomplete. With this change, loci that were sent incorrectly between Oct 8, 2025, and Oct 14, 2025, can be skipped.

1.11.0
----------

Added
~~~~~
- `to_devkit` method to create dictionaries that can be used along the antares-devkit.
- `get_random_loci`, `get_random_locus`, `get_random_locus_ids` and `get_random_locus_id` migrated from devkit to client.

1.10.0
----------

Changed
~~~~~~~
- We stop using setuptools to install the client and started using pyproject.toml with uv.
- Version is now centralized and loaded from `pyproject.toml` and is no longer stored in four files.

Fixed
~~~~~

- Fixed a bug when requirements constraints were ignored when installing the antares-client using pip.

v1.9.0
----------

Changed
~~~~~~~
- Use `U.S. National Science Foundation` and `NSF NOIRLab` throughout the docs and other files as part of NSF rebranding requirements.
- `confluent_kafka` package is now optional. Use `pip install antares-client[subscriptions]` if you need to use a KafkaStreamingClient
 instance.

v1.8.0
----------

Added
~~~~~
- `catalog_search` method to retrieve catalog cross-matching data.

v1.7.0
----------

Added
~~~~~
- `get_catalog_samples` method to retrieve catalog sample data.
- `get_multiple_grav_wave_notices` method to retrieve multiple gravitational wave notices at once
- `get_thumbnails` method to retrieve thumbnails data.

v1.6.0
----------

Added
~~~~~
- `get_latest_grav_wave_notices` and `get_grav_wave_notices` method to get grav wave notices data.

v1.5.0
----------

Added
~~~~~
- `grav_wave_events` property (list[str]) to instances of Locus.

v1.4.0
----------

Added
~~~~~
- ``antares_client.search.get_available_tags`` to get searchable tags.

v1.3.0
----------

Added
~~~~~~~
- `grav_wave_events` property (list[dict]) to instances of Alert.

Changed
~~~~~~~
- All calls to antares APIs will have a timeout of 60 seconds to prevent the client from hanging indefinitely if there are no responses.

v1.2.3
----------

Added
~~~~~~~
- `processed_at` property (datetime) to instances of Alert.

v1.2.2
----------

Changed
~~~~~~~
- Pinned python confluent_kafka library to 1.7.0 to stay with ANTARES version. This prevents deprecation of the TLS certificate lack of verification.

v1.2.1
----------

Fixed
~~~~~

- Documentation for models

v1.2.0
----------

Added
~~~~~

- Support for fetching catalog cross-matches for Loci

Changed
~~~~~~~

- Marked classes in `models.py` as public

v1.1.0
----------

Added
~~~~~

- `coordinates` property (astropy.coordinates.SkyCoord) to instances of Locus

v1.0.6
----------

Changed
~~~~~~~

- Fetch configuration details from the API's /client/config/streaming/default endpoint
  in support of the migration off of Confluent's managed Kafka.

v1.0.5
----------

Changed
~~~~~~~

- Use FQDN, kafka.antares.noirlab.edu, for Kafka connection.

v1.0.4
------

Fixed
~~~~~

- Sorts search results in descending order on the `newest_alert_observation_time`
  property (i.e. latest first).

v1.0.3
------

Fixed
~~~~~

- Set to ignore undefined fields in API payload (allows for decoupling
  version of client from API additions).

v1.0.2
------

Fixed
~~~~~

- Bug where consecutive calls to paginate over all resources at an endpoint repeatedly
  concatenates request query parameters to the URL

Changed
~~~~~~~

- `locus.alerts`, `locus.lightcurve`, `locus.catalogs` are lazy loaded from the API
- Marked private interfaces as private

v1.0.1
------

Fixed
~~~~~

- Removed unnecessarily strict dependency requirements

v1.0.0
------

Added
~~~~~

- Type signatures for most of the library
- ``antares_client.search.cone_search`` for cone searches
- ``antares_client.search.get_by_ztf_object_id`` for lookup by ZTF Object ID

Changed
~~~~~~~

- Removed support for Python 3.4, 3.5
- Interfaces with the API at https://api.antares.noirlab.edu
- Streaming client returns loci instead of alerts
- Search queries hit API directly and no longer need to be prepared server-side

v0.3.2
------

Added
~~~~~

- Better error handling for networking issues in the Client.

v0.3.1
------

Fixed
~~~~~

- Use `time.perf_counter` instead of `time.process_time` for tracking
  timeout values. Fixes #1, where polling a Kafka stream took much
  longer than the specified timeout.

v0.3.0
------

Added
~~~~~

- The ``search`` subcommand, for searching and downloading querysets from the
  ANTARES ElasticSearch database.

- Started using ``click`` for CLI tooling.

- Initial release of documentation.

Fixed
~~~~~

- Verification of SSL certs in requests to the ANTARES portal for thumbnails.

Changed
~~~~~~~

- Renamed CLI ``antares-client`` to ``antares stream``.

v0.2.2
------

Added
~~~~~

- Support for custom Kafka commit behavior.

v0.2.0
------

Added
~~~~~

- ``antares_client.thumbnails`` module for downloading alert thumbnail images.

v0.1.0
------

Fixed
~~~~~

- \#6: ``_locate_ssl_certs_file`` was called in the ``Client`` constructor even
  if an SSL cert path was provided.

v0.0.1
------

Added
~~~~~

- Initial release
