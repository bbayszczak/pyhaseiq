#!/usr/bin/env python
"""Turn a Wireshark JSON export into the readable dialogue committed next to it.

Wireshark writes the WebSocket payloads base64-encoded, one field per frame, and joins the
frames of a single TCP packet with a carriage return. This script decodes them and keeps only
what the protocol analysis needs: who spoke, when, and what was said.

See the "Méthode" section of ``../docs/SPEC-PROTOCOLE-WS.md`` for how to produce the export.

Usage: ``uv run records/extract.py <export.json>`` — writes ``<export.json>.parsed.json``.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from typing import Any

#: Wireshark joins the payloads of several WebSocket frames sharing one TCP packet with this.
FRAME_SEPARATOR = "\r"


def decode_payloads(layers: dict[str, Any]) -> list[str]:
    """Decode every WebSocket payload carried by one captured packet."""
    joined = layers["websocket"]["websocket.payload"]["websocket.payload.text"]
    return [base64.b64decode(chunk).decode() for chunk in joined.split(FRAME_SEPARATOR) if chunk]


def extract(export: Path) -> list[dict[str, Any]]:
    """Read a Wireshark JSON export and return one entry per captured packet."""
    packets = json.loads(export.read_text())
    return [
        {
            "src": packet["_source"]["layers"]["ip"]["ip.src"],
            "dst": packet["_source"]["layers"]["ip"]["ip.dst"],
            "ts": packet["_source"]["layers"]["frame"]["frame.time_utc"],
            "payload": decode_payloads(packet["_source"]["layers"]),
        }
        for packet in packets
    ]


def main() -> None:
    """Parse the export named on the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="Wireshark JSON export to parse")
    export = parser.parse_args().export
    parsed = export.with_name(export.name + ".parsed.json")
    parsed.write_text(json.dumps(extract(export), indent=2))
    print(f"wrote {parsed}")


if __name__ == "__main__":
    main()
