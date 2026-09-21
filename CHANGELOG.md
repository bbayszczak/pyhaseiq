# Changelog

## [0.1.1](https://github.com/bbayszczak/pyhaseiq/compare/v0.1.0...v0.1.1) (2026-09-21)


### Documentation

* translate the whole repository to English ([#6](https://github.com/bbayszczak/pyhaseiq/issues/6)) ([b59c77f](https://github.com/bbayszczak/pyhaseiq/commit/b59c77fb2469007506ac0e313a70582c893e3f3c))

## 0.1.0 (2026-09-21)


### ⚠ BREAKING CHANGES

* the package is now `pyhaseiq`, not `haseiq_connect`, and its API is asynchronous. `get_minimal_temp_percent()` is now `get_heat_up_percent()`, and `get_phase()` returns a `Phase` enum.

### Features

* rewrite as pyhaseiq, a read-only asynchronous library ([5957084](https://github.com/bbayszczak/pyhaseiq/commit/59570847858d51b1fe2591e22260dca1cff2fe84))


### Documentation

* use the manufacturer's own spelling for its name and products ([#2](https://github.com/bbayszczak/pyhaseiq/issues/2)) ([dbd12c4](https://github.com/bbayszczak/pyhaseiq/commit/dbd12c46514735a6c388027a10e0d08e7718dc9e))
