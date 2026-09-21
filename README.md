# pyhaseiq

[![CI](https://img.shields.io/github/actions/workflow/status/bbayszczak/pyhaseiq/ci.yml?branch=main&label=CI)](https://github.com/bbayszczak/pyhaseiq/actions/workflows/ci.yml)
[![Version](https://img.shields.io/github/v/release/bbayszczak/pyhaseiq?label=version)](https://github.com/bbayszczak/pyhaseiq/releases/latest)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Read-only** Python library for Hase iQ wood stoves, over their local WebSocket. Fully local:
no cloud, no vendor app, no account.

> 🔍 **READ-ONLY — THIS LIBRARY COMMANDS NOTHING**
>
> `pyhaseiq` **queries** the stove: temperature, combustion phase, performance. It writes
> nothing, sets nothing, lights nothing, extinguishes nothing. No write command has been
> observed in the protocol, **none is implemented**, and that is a permanent choice of the
> project — see the [prohibitions](CONTRIBUTING.md#prohibitions).
>
> A wood stove is a combustion appliance: operating it stays manual and is the responsibility
> of its user. This library **observes**; it substitutes for no safety device.

> ⚠️ **INDEPENDENT PROJECT, WITH NO AFFILIATION WHATSOEVER**
>
> `pyhaseiq` is **in no way** affiliated with, supported, endorsed or approved by HASE
> Kaminofenbau GmbH, or any of its subsidiaries, brands, related companies, subcontractors or
> partners. *HASE*, *Hase iQ* and *flamemonitor* are trademarks of their respective owners,
> cited solely to describe the hardware this library communicates with, for interoperability
> purposes.
>
> 👉 **Read the full disclaimer below before any use.** It covers the **complete absence of
> warranty**, the **manufacturer's warranty** and the conditions of use. By using this library,
> you acknowledge having read and accepted them.

<details>
<summary><strong>⚠️ Full disclaimer — read before any use</strong></summary>

**This project is entirely independent and is in no way affiliated with, supported,
endorsed or approved by HASE Kaminofenbau GmbH (Niederkircher Straße 14, 54294 Trier,
Amtsgericht Wittlich HRB 4937), or any of its subsidiaries, brands, related companies,
subcontractors or partners.**

*HASE*, *Hase iQ* and *flamemonitor* are trademarks of their respective owners. They are
cited here only to **describe the hardware this library may communicate with**, for
interoperability purposes. No code, binary, firmware, cryptographic key or manufacturer
documentation is reproduced or redistributed in this repository.

**Project name** — `pyhaseiq` is a working name chosen for readability. It carries no
affiliation, and constitutes neither a trademark, nor a claim of origin, nor an
authorisation from the owner of the *Hase* trademark. This library is a third-party
component **compatible with** this hardware, and nothing more.

**Method** — the protocol documented here was reconstructed solely by observing the
network dialogue between the vendor application and a legally acquired stove, on an
installation belonging to the author. No firmware was decompiled, and no manufacturer
cryptographic key was extracted or published. This work falls under the interoperability
exception (art. L122-6-1 III and IV of the French Intellectual Property Code, directive
2009/24/EC art. 5 and 6).

**Read-only** — this library sends no write command to the stove. It changes no setting,
and neither starts nor interrupts any combustion. Operating the stove stays entirely
manual and under the responsibility of its user, in accordance with the manufacturer's
manual.

**No safety role** — the values read are provided for information only. They constitute
neither a certified measurement, nor an alarm, nor a safety device, and are no substitute
whatsoever for a smoke detector, a carbon monoxide detector or the statutory sweeping of
your installation. **Base no safety decision on this library.**

**Use** — this library is intended for reading equipment that you own or are the
legitimate user of, and that alone.

**No warranty** — this software is provided "as is", without warranty of any kind, express
or implied, including but not limited to the warranties of merchantability, fitness for a
particular purpose and non-infringement. To the extent permitted by applicable law, the
author shall not be held liable for any damage whatsoever: malfunction, hardware damage,
data loss, or any direct or indirect damage resulting from the use of this library.

**Manufacturer's warranty** — using this software with your hardware may affect its
warranty. Check before using it.

**Support** — provided on a voluntary basis, with no commitment as to delay or outcome.

**License** — MIT, see [LICENSE](LICENSE).

By using this library, you acknowledge having read and accepted all of these conditions.

</details>

---

## Contents

- [Which generation?](#which-generation)
- [Quick start](#quick-start)
- [Project status](#project-status)
- [Installation](#installation)
- [Usage](#usage)
- [Logging](#logging)
- [Development](#development)
- [Contributing](#contributing)
- [Security](#security)

---

## Which generation?

**Two generations of stoves carry the name "Hase iQ"**, and they do not speak the same
language. They are told apart by the application you use:

| your application | generation | `pyhaseiq` |
|---|---|---|
| **`flamemonitor`** | old | ✅ supported |
| **`HASE iQ`** | new | ❌ not supported |

The new generation has not been observed and its protocol is unknown. Nothing is planned on
that front, and feedback is welcome.

The protocol of the old one is described in full in
[`docs/SPEC-WS-PROTOCOL.md`](docs/SPEC-WS-PROTOCOL.md), where every statement carries a
✅ confirmed / 🟡 partial / ❓ assumed status.

---

## Quick start

With [`uv`](https://docs.astral.sh/uv/) and the IP address of your stove:

```bash
git clone https://github.com/bbayszczak/pyhaseiq
cd pyhaseiq
uv run demo.py 192.168.1.165
```

`uv` creates the environment and installs the dependencies on its own. `demo.py` **writes
nothing**: it displays a continuously refreshed table with the stove's phase and the available
readings. It is the quickest way to check that your stove answers.

---

## Project status

🚧 **Alpha.** Reading works and the protocol is documented. The API may still change.

The changes of each version are recorded in the [CHANGELOG](CHANGELOG.md), kept up to date
automatically from the commit messages.

---

## Installation

```bash
pip install pyhaseiq
```

Or straight from the repository:

```bash
pip install git+https://github.com/bbayszczak/pyhaseiq
```

## Usage

The API is **asynchronous**: the stove is a WebSocket server, and that is the model a host such
as Home Assistant expects.

```python
import asyncio

from pyhaseiq import Client, Phase


async def main() -> None:
    async with Client("192.168.1.165") as stove:
        phase = await stove.get_phase()
        print(phase)  # Phase.HEATING_UP

        if phase is Phase.HEATING_UP:
            print(await stove.get_temperature())  # 163.3 °C in the firebox
            print(await stove.get_heat_up_percent())  # 53.5 % of the heat-up
        elif phase is Phase.NOMINAL:
            print(await stove.get_performance())  # 69 % combustion performance


asyncio.run(main())
```

### The phases

`get_phase()` returns a [`Phase`](src/pyhaseiq/models.py), which is an `IntEnum`:

| value | name | meaning |
|---|---|---|
| `0` | `Phase.IDLE` | no fire, the stove is waiting |
| `1` | `Phase.HEATING_UP` | fire burning, the temperature is rising |
| `2` | `Phase.NOMINAL` | nominal temperature reached |
| `3` | `Phase.NEEDS_WOOD` | wood needs to be added |
| `4` | `Phase.BURNING_OUT` | the fire is dying down, add no more wood |

> ⚠️ **Not every reading is available in every phase.** The vendor application only asks for
> `appT` and `appAufheiz` in phase `HEATING_UP`, and for `appP` in phase `NOMINAL`. Whether the
> stove answers anyway outside those phases or stays silent is unknown — in which case the call
> ends in a `ResponseTimeoutError`. **Test the phase before reading**, as the example above
> does.

### The errors

All of them derive from `HaseIQError`, which makes it possible to catch the whole library with
a single `except`:

| exception | when |
|---|---|
| `ConnectionFailedError` | stove unreachable, or connection lost mid-dialogue |
| `ResponseTimeoutError` | the stove did not answer within the allotted time |
| `ProtocolError` | unreadable answer, or unknown phase |

The client **never reconnects on its own**: it keeps no state, and the retry policy belongs to
the caller. A lost connection stays lost — open a new client.

### Raw requests

The requests that are documented but not exposed through a typed method — the measurement
series, the firmware versions — remain reachable:

```python
await stove.get("_wversion")  # '1.4'
await stove.get("appP30Tx")  # '30'
await stove.get("appP30T[15;29]")  # '41;40;40;40;40;39;...'
```

The names are listed in [`docs/SPEC-WS-PROTOCOL.md`](docs/SPEC-WS-PROTOCOL.md).

### Trying it without writing any code

```bash
uv run demo.py 192.168.1.165                      # continuously refreshed table
uv run demo.py 192.168.1.165 --once               # a single reading
uv run demo.py 192.168.1.165 --request _wversion  # a raw request, repeated
uv run demo.py 192.168.1.165 --debug              # show the WebSocket dialogue
```

Sample output:

```
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ parameter        ┃ value                 ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ Last update      │ 09/21/26 - 08:51:12   │
│ Phase            │ heating up (1)        │
│ Temperature (°C) │ 163.3                 │
│ Heat-up (%)      │ 53.5                  │
│ Performance (%)  │ —                     │
└──────────────────┴───────────────────────┘
```

## Logging

The library uses the standard `logging` module and **configures nothing**: no handler, no
level, no format. The host application decides. Each module has its own logger, named after the
package — `pyhaseiq.client` — which allows filtering on the whole package as well as on a
single module.

Everything is at `DEBUG`: opening the connection, and each request / response pair. Errors are
not logged, they are **raised**; it is up to the caller to decide what to do with them.

In Home Assistant, through `configuration.yaml`:

```yaml
logger:
  logs:
    pyhaseiq: debug
```

In a standalone script:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

Sample trace:

```
DEBUG pyhaseiq.client: connecting to ws://192.168.1.165:8080
DEBUG pyhaseiq.client: appPhase = 1
DEBUG pyhaseiq.client: appT = 163.3
DEBUG pyhaseiq.client: appAufheiz = 53.5
```

The stove exposes no identifier, no key and no personal data: a `DEBUG` trace can be attached
as is to a bug report.

## Development

```bash
uv run ruff check .      # lint
uv run ruff format .     # formatting
uv run pytest            # tests — no hardware required, the stove is faked
```

---

## Contributing

Feedback is welcome, especially about **other stove models** and about the generation driven by
the `HASE iQ` application, which has never been observed.

- **Report a bug or suggest a change** —
  [open an issue](https://github.com/bbayszczak/pyhaseiq/issues/new/choose), stating which
  application you normally drive your stove with.
- **Propose code** — scope, conventions and prohibitions are described in
  [CONTRIBUTING.md](CONTRIBUTING.md), to be read before opening a pull request.

---

## Security

The stove exposes an **unencrypted WebSocket with no authentication whatsoever** on port
`8080`: any machine on your local network can query it. This is not a choice of this library,
it is how the stove is designed.

**Never expose this port on the Internet**, and do not forward it from your router. Leave the
stove on the local network, behind your router.

To report a vulnerability in this library, use the
[private reporting](SECURITY.md) — never a public issue.
