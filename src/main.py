try:
    import orjson as json
except ImportError:
    import json
import dbm
import logging
from httpx import Client, HTTPStatusError, HTTPTransport, RequestError

from settings import settings

# hypercorn logging format
logging.basicConfig(
    level=settings.log_level,
    format="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
)

from app import app 