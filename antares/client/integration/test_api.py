import logging

import antares_client
import antares_client.config
from antares_client import search

API_URL = "https://api.antares.noirlab.edu/v1/"
QUERY = {
    "query": {
        "bool": {
            "filter": {
                "sky_distance": {
                    "distance": "0.002777777777777778 degree",
                    "htm16": {"center": "23:08:0.21 27:25:3.88"},
                }
            }
        }
    }
}

print(f"Testing ANTARES client version {antares_client.__version__}")
print(f"Testing against API at {API_URL}")

logging.basicConfig(level=logging.DEBUG)

antares_client.config.config["ANTARES_API_BASE_URL"] = API_URL

locus = search.get_by_id("ANT2020snzro")
assert locus is not None
assert locus.timeseries is not None
assert locus.lightcurve is not None
assert locus.alerts is not None
assert len(locus.alerts) > 0

loci = list(search.search(QUERY))
assert len(loci) > 0
assert loci[0].timeseries is not None
assert loci[0].lightcurve is not None
assert loci[0].alerts is not None
