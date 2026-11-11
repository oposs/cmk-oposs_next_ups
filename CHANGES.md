# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### New

### Changed

### Fixed
- The Battery State service went CRIT with "UNKNOWN state" when the UPS
  reported its battery status as unknown (value 1). It now goes UNKNOWN,
  as it already did for value 0.
- In a Checkmk GUI set to a language other than English, the
  "Upper levels" and "Lower levels" fields of the NextUPS rules stayed
  in English. They are now translated like the rest of the rule form.

## 0.2.0 - 2026-11-09
### New
- The package carries the release version in its check plugin
  (`__version__`).

### Changed
- Licence is now GNU General Public License v2, matching the headers
  the source files carry. The `LICENSE` file previously held the MIT
  text, which contradicted them.

### Fixed
- A measuring service, such as Battery Temperature, Phase RS Input
  Voltage or Battery Current, showed a crash report when the UPS sent a
  value that is not a number. It now goes UNKNOWN with "the UPS sent no
  number" and the value it got.
- Time On Battery showed short times in hours with one decimal, so two
  minutes on battery read "0.0h (warn/crit at 0.0h/0.1h)". It now shows
  minutes and seconds, such as "2 minutes 0 seconds".
- Battery Time Remaining showed the time in hours with one decimal, so
  its default warning level of 20 minutes read "0.3h". It now shows
  minutes and seconds, such as "19 minutes 0 seconds".

## 0.1.2 - 2026-04-27
### Fixed
- Metric translations for legacy `next_ups_*` history are now keyed on
  the new `oposs_next_ups_*` check commands so they actually fire.
  Previously they were keyed on the now-uninstalled legacy commands and
  Checkmk's translation lookup (an exact match on the live service's
  current check command) silently missed them — leaving the legacy
  generic-named RRD files (`temperature.rrd`, `voltage.rrd`,
  `current.rrd`, `frequency.rrd`, `power.rrd`, `percentage.rrd`,
  `duration.rrd`) orphaned in the per-service directories. After
  upgrading and reloading (`cmk -R` / `omd restart apache`), graphs of
  the new `oposs_next_*` services on hosts that previously ran the
  legacy plugin will show one continuous line spanning the pre- and
  post-upgrade history.

## 0.1.1 - 2026-03-24
### Fixed
- Fix ruleset topic: use `Topic.ENVIRONMENTAL` instead of incorrect `Topic.ENVIRONMENT`

## 0.1.0 - 2026-03-04
### New
- Initial migration from oegig-plugins to Checkmk 2.3.x v2 API
- Data-driven architecture: targets list + closure generates ~44 check plugins
- Graphing definitions for all metric types (temperature, voltage, current,
  frequency, apparent power, true power, load, battery charge, backup time)
- Custom WATO rulesets for configurable thresholds
- Metric names prefixed with `oposs_next_` for namespace isolation
- MKP packaging via oposs/mkp-builder GitHub Action

### Fixed
- "Time On Battery" OID corrected from `s.0` to `2.0` (upsSecondsOnBattery)
- "Output True Power" render unit corrected from kVA to kW (true/active power)
- "Bypass True Power" render unit corrected from kVA to kW
- Battery State map now includes state `0` to prevent KeyError


