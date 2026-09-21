"""Encoding and decoding of the stove's WebSocket payloads — pure functions, no I/O.

The stove speaks a trivial request/response protocol: the client sends ``_req=<name>``, the
stove answers ``<name>=<value>``, and both directions are base64-encoded text frames. One
frame in, exactly one frame out; the stove never speaks first. See
``docs/SPEC-PROTOCOLE-WS.md`` for the full protocol.
"""

from __future__ import annotations

import base64
import binascii

from .exceptions import ProtocolError

#: Prefix the stove expects on every request, before base64 encoding.
REQUEST_PREFIX = "_req="


def encode_request(name: str) -> str:
    """Encode a request name into the base64 text frame the stove expects.

    :param name: request name, e.g. ``appT``
    :return: the base64 payload to send
    """
    return base64.b64encode(f"{REQUEST_PREFIX}{name}".encode()).decode("ascii")


def decode_response(frame: str, name: str) -> str:
    """Decode a base64 response frame and strip the request name the stove echoes back.

    The stove prefixes every answer with the name it was asked for: ``appT`` is answered
    ``appT=163.3``. Only the leading ``<name>=`` is removed — never more, because a value may
    itself contain an ``=`` (``_oemver`` answers ``_oemver=AAF_5815=9``).

    :param frame: the base64 payload received from the stove
    :param name: the request name that was sent, used to validate and strip the prefix
    :return: the value, with the echoed prefix removed
    :raises ProtocolError: if the frame is not base64 UTF-8, or does not echo ``name``
    """
    try:
        decoded = base64.b64decode(frame, validate=True).decode()
    except (binascii.Error, ValueError) as error:
        raise ProtocolError(f"response to {name!r} is not valid base64 UTF-8") from error

    prefix = f"{name}="
    if not decoded.startswith(prefix):
        raise ProtocolError(f"response to {name!r} does not echo it: {decoded!r}")

    # removeprefix, never lstrip: lstrip takes a *character set*, so `"appT=1.4".lstrip("appT=")`
    # would eat any leading `a`, `p`, `T` or `=` of the value itself.
    return decoded.removeprefix(prefix)


def parse_float(value: str, name: str) -> float:
    """Convert a stove value to ``float``, reporting a protocol error rather than ValueError.

    :param value: the raw value returned by the stove
    :param name: the request name, used in the error message
    :return: the value as a float
    :raises ProtocolError: if the value is not a number
    """
    try:
        return float(value)
    except ValueError as error:
        raise ProtocolError(f"{name!r} answered {value!r}, expected a number") from error
