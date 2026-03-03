# NextUPS Checkmk Plugin

Checkmk SNMP plugin for monitoring NextUPS / Winner Pro / Voltronic UPS systems.

## Features

Monitors NextUPS devices via SNMP with ~44 services:

| Category | Services | Thresholds |
|----------|----------|------------|
| Alarms | UPS Alarm Check | State-based |
| Battery Status | Battery State | State-based |
| Battery | Temperature, Voltage, Current, Charge Remaining, Time Remaining, Time On Battery | Configurable |
| Input | Phase RS/ST/TR Voltage, Frequency, Current | Configurable (voltage, frequency) |
| Output | Phase RS/ST/TR Voltage, Frequency, Current | Configurable (voltage, frequency) |
| Output Power | Phase RS/ST/TR Apparent Power, Phase RS/ST/TR True Power | Info only |
| Output Load | Phase RS/ST/TR Load | Configurable |
| Bypass | Phase RS/ST/TR Voltage, Current, True Power | Configurable (voltage) |

All configurable thresholds can be adjusted through Checkmk's WATO GUI.

## SNMP Detection

The plugin detects NextUPS devices where:
- OID `.1.3.6.1.4.1.21111.1.1.1.3.0` starts with `WPHVR3K0`

## Installation

### MKP Package (recommended)

Download the latest `.mkp` file from the
[Releases](https://github.com/oposs/cmk-oposs_next_ups/releases) page and
install it:

```bash
mkp install oposs_next_ups-<version>.mkp
```

### Manual Installation

Copy the plugin files into your Checkmk site:

```
local/lib/python3/cmk_addons/plugins/oposs_next_ups/
├── agent_based/
│   └── oposs_next_ups.py
├── graphing/
│   └── next_ups.py
└── rulesets/
    └── next_ups.py
```

## Troubleshooting

Test SNMP connectivity:

```bash
snmpget -v2c -c <community> <host> .1.3.6.1.4.1.21111.1.1.1.3.0
```

Expected output contains `WPHVR3K0`.

## License

MIT - OETIKER+PARTNER AG
