# cmk-oposs_next_ups

Checkmk SNMP plugin for NextUPS / Winner Pro / Voltronic UPS systems.
Migrated from oegig-plugins to Checkmk 2.3.x v2 API.

## Components

- `local/lib/python3/cmk_addons/plugins/oposs_next_ups/agent_based/oposs_next_ups.py` — SNMP sections + ~44 check plugins
- `local/lib/python3/cmk_addons/plugins/oposs_next_ups/graphing/next_ups.py` — metric, graph, perfometer definitions
- `local/lib/python3/cmk_addons/plugins/oposs_next_ups/rulesets/next_ups.py` — WATO ruleset definitions
- `.mkp-builder.ini` — MKP packaging config
- `.github/workflows/` — repo-infra callers: `ci.yml` (ruff, pytest, MKP build), `changelog.yml`, and the release flow (`release-pr.yml` → `release-build.yml` → `release-publish.yml`); `.github/repo-infra.json` lists the version files and release assets
- `tests/` — pytest suite against the real Checkmk 2.3.0 API (`tests/conftest.py` fetches it into `.cmk-api/`)

## Architecture

- Data-driven design: `targets` list defines all checks declaratively
- `_make_plugins()` closure generates module-level variables via `globals()`
- Each target gets its own `SimpleSNMPSection` + `CheckPlugin`
- Two check patterns: state-mapping (Result) and check_levels (with params)
- `skip_zero` flag on frequency targets: emits NaN when SNMP value is 0 (no input)
- SNMP detection: OID `.1.3.6.1.4.1.21111.1.1.1.3.0` starts with `WPHVR3K0`
- Metric prefix: `oposs_next_`
- Custom WATO rulesets for checks with configurable thresholds
