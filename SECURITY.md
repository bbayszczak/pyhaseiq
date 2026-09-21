# Security policy

## Supported versions

The project is in **alpha**: only the latest released version receives fixes.

## Reporting a vulnerability

**Do not open a public issue for a security flaw.**

Use [GitHub's private reporting](https://github.com/bbayszczak/pyhaseiq/security/advisories/new),
which opens a confidential channel with the maintainers. A first response is aimed at within 7
days.

Please include a description of the problem, the steps to reproduce it and the estimated impact.

## The stove has no authentication

The stove exposes an **unencrypted WebSocket with no authentication** on port `8080`: any
machine on your local network can query it. This library changes nothing about that, it merely
connects to it.

**Never expose this port on the Internet** and do not forward it from your router. The only
protection the stove has is staying on the local network.

This comes from the design of the hardware, not from a flaw in this library: there is no point
reporting it as such.

## Bug reports

Since the library is read-only, its traces contain no identifier, no key and no personal data: a
`DEBUG` trace can be attached as is to an issue.
