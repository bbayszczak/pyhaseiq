"""Value types returned by the client."""

from __future__ import annotations

from enum import IntEnum


class Phase(IntEnum):
    """Operating phase reported by the stove, as answered by ``appPhase``.

    - ``IDLE``: no fire, the stove is waiting for one.
    - ``HEATING_UP``: a fire is going and the temperature is climbing towards the nominal one.
    - ``NOMINAL``: nominal temperature reached, the burn is at its efficient point.
    - ``NEEDS_WOOD``: time to add a log.
    - ``BURNING_OUT``: the fire is dying out — do not add wood any more.

    ``BURNING_OUT`` is the one value never seen in the captures the protocol was reconstructed
    from; it comes from the stove's own documentation. See ``docs/SPEC-PROTOCOLE-WS.md``.
    """

    IDLE = 0
    HEATING_UP = 1
    NOMINAL = 2
    NEEDS_WOOD = 3
    BURNING_OUT = 4
