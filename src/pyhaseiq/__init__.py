"""Read-only Python client for Hase iQ wood stoves, over their local WebSocket.

Independent project, not affiliated with any manufacturer — see the README. This library
**only reads**: it implements no command that changes anything on the stove.

Example:
    >>> import asyncio
    >>> from pyhaseiq import Client
    >>> async def main():  # doctest: +SKIP
    ...     async with Client("192.168.1.165") as stove:
    ...         print(await stove.get_phase(), await stove.get_temperature())
    >>> asyncio.run(main())  # doctest: +SKIP

"""

from __future__ import annotations

import logging

from .client import DEFAULT_PORT, DEFAULT_TIMEOUT, Client
from .exceptions import (
    ConnectionFailedError,
    HaseIQError,
    ProtocolError,
    ResponseTimeoutError,
)
from .models import Phase

# A library must not configure logging: the application owns the handlers and the levels.
# This only keeps the "no handler could be found" warning away when nothing is configured at
# all, as recommended for libraries. Never add a handler, a level or a formatter here.
logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "0.0.0"  # x-release-please-version

__all__ = [
    "DEFAULT_PORT",
    "DEFAULT_TIMEOUT",
    "Client",
    "ConnectionFailedError",
    "HaseIQError",
    "Phase",
    "ProtocolError",
    "ResponseTimeoutError",
]
