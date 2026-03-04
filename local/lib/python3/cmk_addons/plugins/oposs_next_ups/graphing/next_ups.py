#!/usr/bin/env python3

from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import (
    Color,
    DecimalNotation,
    Metric,
    Unit,
)
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.perfometers import Perfometer, FocusRange, Closed

# Units
unit_celsius = Unit(DecimalNotation("\u00b0C"))
unit_percent = Unit(DecimalNotation("%"))
unit_volts = Unit(DecimalNotation("V"))
unit_amperes = Unit(DecimalNotation("A"))
unit_hertz = Unit(DecimalNotation("Hz"))
unit_watts = Unit(DecimalNotation("W"))
unit_va = Unit(DecimalNotation("VA"))
unit_seconds = Unit(DecimalNotation("s"))

# Metrics
metric_oposs_next_temperature = Metric(
    name="oposs_next_temperature",
    title=Title("Temperature"),
    unit=unit_celsius,
    color=Color.ORANGE,
)

metric_oposs_next_voltage = Metric(
    name="oposs_next_voltage",
    title=Title("Voltage"),
    unit=unit_volts,
    color=Color.BLUE,
)

metric_oposs_next_current = Metric(
    name="oposs_next_current",
    title=Title("Current"),
    unit=unit_amperes,
    color=Color.GREEN,
)

metric_oposs_next_frequency = Metric(
    name="oposs_next_frequency",
    title=Title("Frequency"),
    unit=unit_hertz,
    color=Color.PURPLE,
)

metric_oposs_next_apparent_power = Metric(
    name="oposs_next_apparent_power",
    title=Title("Apparent Power"),
    unit=unit_va,
    color=Color.YELLOW,
)

metric_oposs_next_true_power = Metric(
    name="oposs_next_true_power",
    title=Title("True Power"),
    unit=unit_watts,
    color=Color.DARK_YELLOW,
)

metric_oposs_next_load_pct = Metric(
    name="oposs_next_load_pct",
    title=Title("Load"),
    unit=unit_percent,
    color=Color.RED,
)

metric_oposs_next_battery_pct = Metric(
    name="oposs_next_battery_pct",
    title=Title("Battery Charge"),
    unit=unit_percent,
    color=Color.GREEN,
)

metric_oposs_next_time_remaining = Metric(
    name="oposs_next_time_remaining",
    title=Title("Battery Time Remaining"),
    unit=unit_seconds,
    color=Color.BLUE,
)

metric_oposs_next_time_on_battery = Metric(
    name="oposs_next_time_on_battery",
    title=Title("Time On Battery"),
    unit=unit_seconds,
    color=Color.DARK_BLUE,
)

# Graphs
graph_oposs_next_temperature = Graph(
    name="oposs_next_temperature",
    title=Title("NextUPS Temperature"),
    simple_lines=["oposs_next_temperature"],
    minimal_range=MinimalRange(lower=0, upper=80),
)

graph_oposs_next_voltage = Graph(
    name="oposs_next_voltage",
    title=Title("NextUPS Voltage"),
    simple_lines=["oposs_next_voltage"],
)

graph_oposs_next_current = Graph(
    name="oposs_next_current",
    title=Title("NextUPS Current"),
    simple_lines=["oposs_next_current"],
)

graph_oposs_next_frequency = Graph(
    name="oposs_next_frequency",
    title=Title("NextUPS Frequency"),
    simple_lines=["oposs_next_frequency"],
    minimal_range=MinimalRange(lower=45, upper=55),
)

graph_oposs_next_apparent_power = Graph(
    name="oposs_next_apparent_power",
    title=Title("NextUPS Apparent Power"),
    simple_lines=["oposs_next_apparent_power"],
)

graph_oposs_next_true_power = Graph(
    name="oposs_next_true_power",
    title=Title("NextUPS True Power"),
    simple_lines=["oposs_next_true_power"],
)

graph_oposs_next_load_pct = Graph(
    name="oposs_next_load_pct",
    title=Title("NextUPS Load"),
    simple_lines=["oposs_next_load_pct"],
    minimal_range=MinimalRange(lower=0, upper=100),
)

graph_oposs_next_battery_pct = Graph(
    name="oposs_next_battery_pct",
    title=Title("NextUPS Battery Charge"),
    simple_lines=["oposs_next_battery_pct"],
    minimal_range=MinimalRange(lower=0, upper=100),
)

graph_oposs_next_time_remaining = Graph(
    name="oposs_next_time_remaining",
    title=Title("NextUPS Battery Time Remaining"),
    simple_lines=["oposs_next_time_remaining"],
)

graph_oposs_next_time_on_battery = Graph(
    name="oposs_next_time_on_battery",
    title=Title("NextUPS Time On Battery"),
    simple_lines=["oposs_next_time_on_battery"],
)

# Perfometers
perfometer_oposs_next_load_pct = Perfometer(
    name="oposs_next_load_pct",
    focus_range=FocusRange(lower=Closed(0), upper=Closed(100)),
    segments=["oposs_next_load_pct"],
)

perfometer_oposs_next_battery_pct = Perfometer(
    name="oposs_next_battery_pct",
    focus_range=FocusRange(lower=Closed(0), upper=Closed(100)),
    segments=["oposs_next_battery_pct"],
)
