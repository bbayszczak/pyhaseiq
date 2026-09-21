# Contributing

## Scope

`pyhaseiq` is a **read-only** and **stateless** library for Hase iQ stoves of the
`flamemonitor` generation. It queries the stove and returns what it answers. Nothing else.

History, averages, thresholds, notifications, automatic reconnection: all of that belongs to
the calling layer — typically a Home Assistant integration. Proposals that bring state back in
here will be turned down.

## Getting started

```bash
uv run ruff check .      # lint
uv run ruff format .     # formatting
uv run pytest            # tests — no hardware required, the stove is faked
```

Python ≥ 3.13. Always go through `uv`. The linter is strict on `src/` (docstrings and
annotations are mandatory); tests are exempt.

## Conventions

- Commits follow [Conventional Commits](https://www.conventionalcommits.org/), in English.
  `release-please` relies on them: only `feat:` and `fix:` trigger a release.
- Everything is written in English: documentation, code and docstrings.
- The protocol is described in [`docs/SPEC-WS-PROTOCOL.md`](docs/SPEC-WS-PROTOCOL.md), where
  every statement carries a ✅ confirmed / 🟡 partial / ❓ assumed status. **Never write code on
  the strength of a ❓ point**: confirm it on real hardware first, and update the spec.
- GitHub actions are pinned to full SHAs; Dependabot updates them. Never go back to a moving
  tag.

## Prohibitions

A wood stove is a combustion appliance installed in someone's home. These points will not be
merged:

- ⛔ **No writing to the stove.** No write command has been observed in the protocol, none is
  implemented, and that is a permanent choice. A read-only library cannot break anything; as
  soon as it writes, that guarantee is gone.
- ⛔ **Do not sweep request names at random** on a real stove. What an unknown `_req=` triggers
  in the firmware is unknown. New names are discovered by observing the vendor application, not
  by guessing.
- ⛔ **Do not bring state back** into the library: no history, no cache, no average, no
  automatic reconnection.
- ⛔ **Do not present the values read as a safety measure.** They are indicative and replace
  neither any detector nor any maintenance obligation.

## Legal terms of contributions

By contributing to this repository, you accept the following.

1. **No proprietary code** — you must not submit any code, firmware or other material belonging
   to the manufacturer or to a third party. Contributions must be original or under a licence
   compatible with this project's.

2. **No protected material** — no dumps, no decompiled binaries, no cryptographic keys, and no
   content obtained in breach of an end-user licence agreement (EULA), a non-disclosure
   agreement (NDA) or an equivalent restriction.

3. **Independent work** — contributions must result from independent analysis and development.
   If you relied on reverse engineering, it must have been carried out lawfully and for
   interoperability purposes only.

4. **Licence compatibility** — every contribution is published under the project's licence. By
   submitting code, you confirm that you have the right to do so.

Any pull request that breaches these terms will be rejected. The maintainers reserve the right
to withdraw a contribution that would expose the project to legal risk.

## Security

To report a vulnerability, see [SECURITY.md](SECURITY.md) — never a public issue.
