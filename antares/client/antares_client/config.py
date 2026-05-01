import os

config = {
    "ANTARES_API_BASE_URL": os.getenv(
        "ANTARES_API_BASE_URL", "https://api.antares.noirlab.edu/v1/"
    ),
    "API_TIMEOUT": int(os.getenv("API_TIMEOUT", 60)),
}
