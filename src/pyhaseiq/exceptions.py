"""Exceptions raised by :mod:`pyhaseiq`.

Every error the library raises derives from :class:`HaseIQError`, so a caller — typically a
Home Assistant integration — can catch the whole library with a single ``except``.
"""

from __future__ import annotations


class HaseIQError(Exception):
    """Base class for every error raised by this library."""


class ConnectionFailedError(HaseIQError):
    """The WebSocket could not be opened, or the dialogue was cut short.

    The client never reconnects on its own: it is stateless by design, and the caller owns
    the retry policy. Receiving this means the connection is gone — open a new client.
    """


class ResponseTimeoutError(HaseIQError):
    """The stove did not answer within the configured timeout."""


class ProtocolError(HaseIQError):
    """The stove answered something this library cannot make sense of.

    Either the frame was not valid base64 UTF-8, or it did not echo the request name, or the
    value did not convert to the expected type.
    """
