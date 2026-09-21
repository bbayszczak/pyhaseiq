#!/usr/bin/env python
"""Read a Hase IQ stove and show what it answers.

**This script only reads.** Nothing it does can change anything on the stove — the protocol
carries no write command and none is implemented.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime

from rich.console import Console
from rich.live import Live
from rich.table import Table

from pyhaseiq import Client, HaseIQError, Phase

_LOGGER = logging.getLogger("demo")

#: Shown instead of a value the stove does not report in its current phase.
UNAVAILABLE = "—"

PHASE_LABELS = {
    Phase.IDLE: "no fire",
    Phase.HEATING_UP: "heating up",
    Phase.NOMINAL: "nominal temperature",
    Phase.NEEDS_WOOD: "needs wood",
    Phase.BURNING_OUT: "burning out",
}

#: Label, phases in which to ask, and the reading itself. The phases are the ones in which the
#: vendor app asks for that value; outside them the stove has never been seen answering, so
#: asking would only burn the timeout on every refresh.
READINGS: tuple[tuple[str, frozenset[Phase], Callable[[Client], Awaitable[float]]], ...] = (
    ("Temperature (°C)", frozenset({Phase.HEATING_UP}), Client.get_temperature),
    ("Heat-up (%)", frozenset({Phase.HEATING_UP}), Client.get_heat_up_percent),
    ("Performance (%)", frozenset({Phase.NOMINAL}), Client.get_performance),
)


async def _optional(reading: Awaitable[float]) -> str:
    """Await one reading, turning any stove error into a dash rather than stopping the demo."""
    try:
        return f"{await reading:g}"
    except HaseIQError as error:
        _LOGGER.debug("reading unavailable: %s", error)
        return UNAVAILABLE


async def read(client: Client) -> dict[str, str]:
    """Read every measurement the stove reports in its current phase."""
    phase = await client.get_phase()
    readings = {"Phase": f"{PHASE_LABELS[phase]} ({phase.value})"}
    for label, phases, reading in READINGS:
        # `reading(client)` is only evaluated when the phase matches, so no coroutine is
        # created and left un-awaited.
        readings[label] = await _optional(reading(client)) if phase in phases else UNAVAILABLE
    return readings


def build_table(readings: dict[str, str]) -> Table:
    """Render a set of readings as a two-column table."""
    table = Table()
    table.add_column("parameter")
    table.add_column("value")
    table.add_row("Last update", datetime.now().strftime("%x - %X"))
    for parameter, value in readings.items():
        table.add_row(parameter, value)
    return table


async def run_live(client: Client, interval: float) -> None:
    """Refresh the readings until interrupted."""
    with Live(build_table(await read(client)), refresh_per_second=4) as live:
        while True:
            await asyncio.sleep(interval)
            live.update(build_table(await read(client)))


async def run_raw(client: Client, names: list[str], console: Console) -> None:
    """Send raw requests and print the answers, for exploring the protocol."""
    for name in names:
        try:
            console.print(f"{name} = {await client.get(name)}")
        except HaseIQError as error:
            console.print(f"{name}: [red]{error}[/red]")


def parse_args() -> argparse.Namespace:
    """Build the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="IP address or hostname of the stove")
    parser.add_argument("--port", type=int, default=8080, help="WebSocket port (default: 8080)")
    parser.add_argument("--timeout", type=float, default=5.0, help="seconds to wait for an answer")
    parser.add_argument("--interval", type=float, default=1.0, help="seconds between refreshes")
    parser.add_argument("--once", action="store_true", help="read once and exit")
    parser.add_argument(
        "--request",
        metavar="NAME",
        action="append",
        help="send a raw request instead of the usual readings; repeatable "
        "(names are listed in docs/SPEC-PROTOCOLE-WS.md)",
    )
    parser.add_argument("--debug", action="store_true", help="show the WebSocket dialogue")
    return parser.parse_args()


async def main() -> None:
    """Connect to the stove and run whichever mode was asked for."""
    args = parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(name)s: %(message)s")
    console = Console()
    async with Client(args.host, args.port, args.timeout) as client:
        if args.request:
            await run_raw(client, args.request, console)
        elif args.once:
            console.print(build_table(await read(client)))
        else:
            await run_live(client, args.interval)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except HaseIQError as error:
        raise SystemExit(f"error: {error}") from error
