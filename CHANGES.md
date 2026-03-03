# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### New

- Initial migration from oegig-plugins to Checkmk 2.3.x v2 API
- Data-driven architecture: targets list + closure generates ~44 check plugins
- Graphing definitions for all metric types (temperature, voltage, current,
  frequency, apparent power, true power, load, battery charge, backup time)
- Custom WATO rulesets for configurable thresholds
- Metric names prefixed with `oposs_next_` for namespace isolation
- MKP packaging via oposs/mkp-builder GitHub Action

### Changed

### Fixed

- "Time On Battery" OID corrected from `s.0` to `2.0` (upsSecondsOnBattery)
- "Output True Power" render unit corrected from kVA to kW (true/active power)
- "Bypass True Power" render unit corrected from kVA to kW
- Battery State map now includes state `0` to prevent KeyError
