# Changelog

## 0.1.0 (2026-09-21)


### ⚠ BREAKING CHANGES

* the package is now `pyhaseiq`, not `haseiq_connect`, and its API is asynchronous. `get_minimal_temp_percent()` is now `get_heat_up_percent()`, and `get_phase()` returns a `Phase` enum.

### Features

* rewrite as pyhaseiq, a read-only asynchronous library ([fd35203](https://github.com/bbayszczak/pyhaseiq/commit/fd35203fb198a45093572e4a4131e8fb6a18f20d))


### Documentation

* use the manufacturer's own spelling for its name and products ([#2](https://github.com/bbayszczak/pyhaseiq/issues/2)) ([b4656e1](https://github.com/bbayszczak/pyhaseiq/commit/b4656e11ed92f7e9d6d03aa12da0eb4bd16ada96))
