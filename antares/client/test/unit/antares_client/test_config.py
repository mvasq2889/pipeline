import os
from importlib import reload

from antares_client import config


class TestConfig:
    def test_reads_environment_variable(self):
        dev_url = "https://api.development.antares.noirlab.edu/v1/"
        os.environ["ANTARES_API_BASE_URL"] = dev_url
        os.environ["API_TIMEOUT"] = "1"
        reload(config)
        assert config.config["ANTARES_API_BASE_URL"] == dev_url
        assert config.config["API_TIMEOUT"] == 1
        del os.environ["ANTARES_API_BASE_URL"]
        del os.environ["API_TIMEOUT"]
        reload(config)

    def test_return_default_values(self):
        assert (
            config.config["ANTARES_API_BASE_URL"]
            == "https://api.antares.noirlab.edu/v1/"
        )
        assert config.config["API_TIMEOUT"] == 60
