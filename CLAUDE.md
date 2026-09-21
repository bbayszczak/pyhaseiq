# CLAUDE.md

Context for Claude Code on this repository.

## The project

`pyhaseiq` is a **read-only** library for **Hase iQ wood stoves of the `flamemonitor`
generation**, over their local WebSocket. Nothing else.

⚠️ **Two generations carry the name "Hase iQ".** Only the old one, driven by the `flamemonitor`
application, is supported; the one of the `HASE iQ` application has never been observed. Never
imply in the documentation or in the code that the new one works.

The protocol is described in full in [`docs/SPEC-WS-PROTOCOL.md`](docs/SPEC-WS-PROTOCOL.md),
reconstructed by reverse engineering from network captures that are **not committed**: they
carry the MAC addresses of the real hardware. Every statement there carries a ✅ confirmed /
🟡 partial / ❓ assumed status: refer to it before implementing anything, and never write code
on the strength of a ❓ point.

## Structure

```
src/pyhaseiq/
  protocol.py    base64 encoding and parsing — pure functions, no I/O
  client.py      asynchronous client, serialises the dialogue
  models.py      Phase
  exceptions.py
tests/
  fake.py        fake stove (WebSocket server) replaying the real answers
docs/
  SPEC-WS-PROTOCOL.md
tools/
  extract.py     decodes a Wireshark export into a readable dialogue
demo.py          demonstration script, read-only
```

## Commands

```bash
uv run ruff check .      # lint
uv run ruff format .     # formatting
uv run pytest            # tests, no hardware
uv run demo.py <ip>      # live reading on a real stove
```

Always go through `uv`. Python ≥ 3.13, CI on 3.13 and 3.14.

## Conventions

- **Commits in Conventional Commits**, in English. `release-please` uses them to produce the
  CHANGELOG and the version: only `feat:` and `fix:` trigger a release.
- **Everything is written in English**: documentation, code and docstrings. The stove is also
  sold outside France.
- **Logging**: standard `logging`, one `_LOGGER = logging.getLogger(__name__)` per module and
  **no configuration whatsoever** (no handler, no level, no format) — the host, typically Home
  Assistant, owns the handlers and filters on `pyhaseiq.<module>`. Everything at `DEBUG`, with
  lazy formatting (`_LOGGER.debug("%s = %s", name, value)`), never an f-string — the ruff `LOG`
  and `G` rules check this. Errors are raised, not logged: logging *and* raising produces a
  duplicate in the caller's logs.
- The linter is strict (docstrings and annotations are mandatory in `src/`); tests are exempt
  through `per-file-ignores`.
- GitHub actions are **pinned to full SHAs** (a tag such as `@v4` can be moved onto another
  commit). Dependabot updates them; never go back to a moving tag.
- Public repository: `CONTRIBUTING.md` and `SECURITY.md` are authoritative on the contributor
  side, keep them consistent with this file — in particular the list of prohibitions below.
- `uv.lock` carries the package version: the release workflow resyncs it on the release PR
  branch. Do not edit it by hand, run `uv lock` after any change of version or dependency.
- Merging a release PR publishes the package on **PyPI** through *Trusted Publishing* (OIDC):
  no API token is stored, the authorisation lives in the *publisher* declared on the PyPI side
  (repository `bbayszczak/pyhaseiq`, workflow `release.yml`). Renaming that file or the
  repository breaks publishing until the *publisher* is updated.
- The release workflow deliberately separates `build` and `publish`: `uv build` runs
  third-party code (hatchling and its dependencies) and must never run in the job that carries
  `id-token: write`, otherwise a compromised build dependency could publish to PyPI. Do not
  merge those two jobs back together.
- `release-please` runs under the identity of a dedicated **GitHub App**, never under the
  `GITHUB_TOKEN`: the latter cannot open a PR as long as the repository's "Allow GitHub Actions
  to create and approve pull requests" setting is unchecked, and its writes trigger no
  workflow — so the release PR would never get the checks that main's ruleset requires and
  would stay unmergeable. Its credentials live in the `RELEASE_PLEASE_CLIENT_ID` and
  `RELEASE_PLEASE_PRIVATE_KEY` secrets. The first carries the App's **Client ID** (`Iv23li…`),
  not its numeric App ID: the action's `app-id` entry is deprecated and `client-id` expects the
  other value.
- The commit that resyncs `uv.lock` is created by **the GitHub API**, never by a `git commit`
  in the *runner*: `main` requires verified signatures, and a commit crafted in the runner is
  unsigned and blocks the merge of the release PR. GitHub signs the commits that go through its
  API, and the call carries the App token, so the CI does get triggered again.

## Design principles

- **Read-only, definitively.** No write command has been observed in the protocol and none is
  implemented. That is the central guarantee of the project: a library that only reads cannot
  break anything on a combustion appliance installed in someone's home. Never chip away at it,
  not even "just to test".
- **The client knows no state.** No cache, no history, no automatic reconnection. A lost
  connection stays lost and the caller opens a new one. Any history, average or retry policy
  belongs to the calling layer.
- **Strictly serialised dialogue.** The protocol has no correlation identifier: nothing ties an
  answer to its request but order. Hence the lock in `Client.get()`. The test
  `test_concurrent_readings_are_serialised_and_never_swap_answers` guards the property — it
  fails if the lock is removed.
- **Asynchronous core, assumed**: the stove is a WebSocket server and the target is Home
  Assistant. No synchronous facade.

## Pitfalls of the protocol

- **The prefix is stripped with `removeprefix`, never with `lstrip`.** `lstrip` takes a *set of
  characters*: `"appT=appT".lstrip("appT=")` returns `""`. This is a real bug fixed here,
  guarded by `test_the_prefix_is_removed_as_a_prefix_not_as_a_character_set`.
- **The value may contain an `=`**: `_oemver` answers `_oemver=AAF_5815=9`. Split on the first
  one only.
- **Not every reading is available in every phase.** The vendor application only asks for `appT`
  and `appAufheiz` in phase `HEATING_UP`, and `appP` in phase `NOMINAL`. Whether the stove
  answers outside that phase or stays silent is unknown — in which case the call ends in
  `ResponseTimeoutError`. Test the phase before reading.
- **Phase `4` has never been observed**: it comes from the stove's documentation.

## What not to do

- ⛔ **Never implement or send a write command** to the stove.
- ⛔ **Do not sweep request names at random** on a real stove: what an unknown `_req=` triggers
  in the firmware is unknown.
- ⛔ **Do not recompute `appAufheiz` from `appT`.** The correlation is strong (R² = 0.992) but
  not exact: the stove mixes something else into it.
- ⛔ **Do not present the values read as a safety device** — neither in the code nor in the
  documentation. They are indicative.
- ⛔ **Never commit a raw network capture** — a `.pcap`, a Wireshark export, or the output of
  `tools/extract.py`. An Ethernet capture carries the **MAC addresses** of the stove and of the
  phone, which are permanent hardware identifiers. `records/` is in `.gitignore` for that
  reason; do not take it out.

## Security

The stove has **no authentication**: its WebSocket is open to the whole local network. That is a
fact about the hardware, not a flaw in this library. The documentation must say so and remind
the reader never to expose port `8080` on the Internet.

The traces contain no identifier, no key and no personal data: there is nothing to redact in the
logs, unlike other home-automation protocols. If a secret-bearing request were ever to appear,
this assessment would have to be revisited.

This holds for the library's traces, **not for the network captures** the spec comes from: at
the Ethernet level, they carry the hardware's MAC addresses. They stay out of the repository.
