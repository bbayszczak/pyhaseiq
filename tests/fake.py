"""A fake stove: a local WebSocket server replaying the answers seen in `records/`.

Every value below was read from a real capture, so the tests exercise the parsing against
what the hardware actually sends — including `_oemver`, whose value carries a second `=`.
"""

from __future__ import annotations

import asyncio
import base64
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass

from websockets.asyncio.server import ServerConnection, serve

# Real answers, taken from records/*.parsed.json.
RESPONSES: Mapping[str, str] = {
    "appPhase": "2",
    "appT": "163.3",
    "appP": "69",
    "appAufheiz": "53.5",
    "appErr": "0",
    "appNach": "0",
    "_l1h": "(?)",
    "_oemdev": "2",
    "_oemver": "AAF_5815=9",  # the value itself contains an '='
    "_wversion": "1.4",
    "appP30Tx": "30",
    "appP30T[15;29]": "41;40;40;40;40;39;39;39;39;39;38;38;38;70;13",
}


@dataclass(frozen=True)
class FakeStove:
    """Where the fake stove listens."""

    host: str
    port: int


@asynccontextmanager
async def fake_stove(
    responses: Mapping[str, str] = RESPONSES,
    *,
    encode: bool = True,
) -> AsyncIterator[FakeStove]:
    """Run a fake stove for the duration of the block.

    A request whose name is missing from `responses` gets **no answer at all**, which is how
    the client's timeout is exercised. With `encode=False` the values are sent raw instead of
    being base64 encoded, to exercise the protocol errors.
    """

    async def handler(connection: ServerConnection) -> None:
        async for frame in connection:
            request = base64.b64decode(frame).decode()
            name = request.removeprefix("_req=")
            if name not in responses:
                continue
            value = responses[name]
            answer = f"{name}={value}" if encode else value
            await connection.send(base64.b64encode(answer.encode()).decode() if encode else answer)

    async with serve(handler, "127.0.0.1", 0) as server:
        host, port = server.sockets[0].getsockname()[:2]
        yield FakeStove(host=host, port=port)


async def unreachable_port() -> int:
    """Return a port nothing listens on, to exercise connection failures."""
    loop = asyncio.get_running_loop()
    server = await loop.create_server(asyncio.Protocol, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    server.close()
    await server.wait_closed()
    return port
