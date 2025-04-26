import os

# Application settings
APP_NAME = "Workflow Engine"
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

# Redis settings
REDIS_HOST = os.getenv("REDIS_HOST", "redis-19739.c327.europe-west1-2.gce.redns.redis-cloud.com")
REDIS_PORT = int(os.getenv("REDIS_PORT", 19739))
REDIS_USERNAME = os.getenv("REDIS_USERNAME", "default")
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "b9dCGzitE7KaBtlSIxkJa4STEDqnVZgL")
REDIS_URL = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

# Workflow settings
MAX_CONCURRENT_WORKFLOWS = int(os.getenv("MAX_CONCURRENT_WORKFLOWS", 10))