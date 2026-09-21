"""Read-only asynchronous client for a Hase iQ stove."""

from __future__ import annotations

import asyncio
import logging
from typing import Self

from websockets.asyncio.client import ClientConnection
from websockets.asyncio.client import connect as ws_connect
from websockets.exceptions import WebSocketException

from .exceptions import ConnectionFailedError, ProtocolError, ResponseTimeoutError
from .models import Phase
from .protocol import decode_response, encode_request, parse_float

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 8080
DEFAULT_TIMEOUT = 5.0


class Client:
    """A read-only connection to a Hase iQ stove.

    **This client only reads.** The protocol carries no command that changes anything on the
    stove, and none is implemented here: every method asks a question and returns an answer.

    The dialogue is strictly sequential — the stove answers one frame per frame received, with
    nothing to correlate a response to its request — so a lock serialises it. Concurrent
    ``await``s on the same client are therefore safe; they queue.

    The client holds no state beyond its socket and never reconnects on its own. Once a
    connection is lost it stays lost, and the caller opens a new client.

    Example:
        >>> async with Client("192.168.1.165") as stove:  # doctest: +SKIP
        ...     print(await stove.get_phase())
        ...     print(await stove.get_temperature())

    """

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Prepare a client. Nothing is opened until :meth:`connect` is awaited.

        :param host: IP address or hostname of the stove
        :param port: WebSocket port, ``8080`` on every stove observed so far
        :param timeout: seconds to wait for the connection, and for each answer
        """
        self._host = host
        self._port = port
        self._timeout = timeout
        self._connection: ClientConnection | None = None
        self._lock = asyncio.Lock()

    @property
    def url(self) -> str:
        """The WebSocket URL this client talks to. Unencrypted: the stove offers nothing else."""
        return f"ws://{self._host}:{self._port}"

    async def connect(self) -> None:
        """Open the WebSocket. Awaiting this on an already-connected client is a no-op.

        :raises ConnectionFailedError: if the stove cannot be reached
        """
        if self._connection is not None:
            return
        _LOGGER.debug("connecting to %s", self.url)
        try:
            async with asyncio.timeout(self._timeout):
                self._connection = await ws_connect(self.url)
        except TimeoutError as error:
            raise ConnectionFailedError(f"timed out connecting to {self.url}") from error
        except (OSError, WebSocketException) as error:
            raise ConnectionFailedError(f"cannot connect to {self.url}: {error}") from error

    async def close(self) -> None:
        """Close the WebSocket. Awaiting this on a closed client is a no-op."""
        if self._connection is None:
            return
        _LOGGER.debug("closing %s", self.url)
        connection, self._connection = self._connection, None
        await connection.close()

    async def __aenter__(self) -> Self:
        """Open the connection and return the client."""
        await self.connect()
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        """Close the connection, whatever happened inside the block."""
        await self.close()

    async def get(self, name: str) -> str:
        """Send one raw request and return the stove's answer, prefix stripped.

        Exposed so that requests documented but not wrapped in a typed method — the measurement
        series, the firmware versions — stay reachable without patching the library. Names are
        listed in ``docs/SPEC-WS-PROTOCOL.md``.

        :param name: request name, e.g. ``appT`` or ``_wversion``
        :return: the value the stove answered
        :raises ConnectionFailedError: if the client is not connected, or the socket dies
        :raises ResponseTimeoutError: if the stove stays silent
        :raises ProtocolError: if the answer is unreadable or does not echo ``name``
        """
        if self._connection is None:
            raise ConnectionFailedError("not connected: await connect() first")

        # One request in flight at a time. The protocol has no request id, so two overlapping
        # exchanges would hand each other's answer back.
        async with self._lock:
            connection = self._connection
            try:
                async with asyncio.timeout(self._timeout):
                    await connection.send(encode_request(name))
                    frame = await connection.recv()
            except TimeoutError as error:
                raise ResponseTimeoutError(f"no answer to {name!r} in {self._timeout}s") from error
            except (OSError, WebSocketException) as error:
                raise ConnectionFailedError(f"connection lost asking {name!r}: {error}") from error

        # The stove sends text frames; a binary one would still be a valid base64 payload.
        if isinstance(frame, bytes | bytearray):
            frame = frame.decode("ascii", "replace")
        value = decode_response(frame, name)
        _LOGGER.debug("%s = %s", name, value)
        return value

    async def get_temperature(self) -> float:
        """Read the temperature inside the stove, in degrees Celsius.

        Only meaningful while a fire is going: the stove answers nothing useful when idle.

        :return: the temperature in °C
        """
        return parse_float(await self.get("appT"), "appT")

    async def get_phase(self) -> Phase:
        """Read the operating phase of the stove.

        :return: the current :class:`~pyhaseiq.models.Phase`
        :raises ProtocolError: if the stove reports a phase this library does not know
        """
        value = await self.get("appPhase")
        try:
            return Phase(int(value))
        except ValueError as error:
            raise ProtocolError(f"unknown phase {value!r}") from error

    async def get_performance(self) -> float:
        """Read the combustion performance index, as a percentage.

        Only answered once the nominal temperature is reached.

        :return: the performance index
        """
        return parse_float(await self.get("appP"), "appP")

    async def get_heat_up_percent(self) -> float:
        """Read how far the stove is through its heat-up, as a percentage.

        ``appAufheiz`` — *Aufheizen*, "to heat up" in German. Only answered while the
        temperature is climbing, never once the nominal one is reached.

        :return: progress towards the nominal temperature, from 0 to 100
        """
        return parse_float(await self.get("appAufheiz"), "appAufheiz")
