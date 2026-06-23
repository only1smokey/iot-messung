# install rich linux: sudo apt install python3-rich
# run here in this folder: python auswertung.py

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:
    print("Rich fehlt. Install: sudo apt install python3-rich")
    raise SystemExit(1)

project_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_dir))

# use same db code like website
from db import get_averages, get_readings

console = Console()

METRICS = [
    ("Temperatur", "temperature", "C"),
    ("Feuchtigkeit", "humidity", "%"),
    ("Luftdruck", "pressure", "hPa"),
]


def average(rows, key):
    # average make
    if not rows:
        return None

    return sum(row[key] for row in rows) / len(rows)


def show_number(value, unit):
    # number pretty
    if value is None:
        return "--"

    return f"{value:.2f} {unit}"


def trend(rows, key):
    # old half vs new half
    if len(rows) < 2:
        return "--"

    middle = len(rows) // 2
    old = average(rows[:middle], key)
    new = average(rows[middle:], key)
    diff = new - old

    if abs(diff) < 0.05:
        return "same"
    if diff > 0:
        return f"up +{diff:.2f}"
    return f"down {diff:.2f}"


def parse_time(row):
    # text time to real time
    return datetime.fromisoformat(row["created_at"])


def add_average_row(table, name, rows):
    values = [show_number(average(rows, key), unit) for _, key, unit in METRICS]
    table.add_row(name, str(len(rows)), *values)


def build_average_table(all_average, readings):
    table = Table(title="Auswertung")
    table.add_column("Bereich")
    table.add_column("Anzahl")
    table.add_column("Temperatur")
    table.add_column("Feuchtigkeit")
    table.add_column("Luftdruck")

    if all_average:
        table.add_row(
            "Alle Daten",
            str(all_average["count"]),
            show_number(all_average["temperature"], "C"),
            show_number(all_average["humidity"], "%"),
            show_number(all_average["pressure"], "hPa"),
        )

    for amount in (5, 10, 30):
        add_average_row(table, f"Letzte {amount}", readings[-amount:])

    if readings:
        newest_time = parse_time(readings[-1])

        for minutes, label in ((15, "Letzte 15 min"), (60, "Letzte 1 h"), (1440, "Letzte 24 h")):
            start_time = newest_time - timedelta(minutes=minutes)
            rows = [row for row in readings if parse_time(row) >= start_time]
            add_average_row(table, label, rows)

    return table


def build_trend_table(readings):
    table = Table(title="Trend")
    table.add_column("Wert")
    table.add_column("Richtung")

    for name, key, _ in METRICS:
        table.add_row(name, trend(readings, key))

    return table


def print_report():
    # ask db stuff
    readings = get_readings(200)
    all_average = get_averages()

    console.clear()
    console.print(Panel("Auswertung laeuft. Stop mit STRG+C.", title="Manual Script"))

    if not readings:
        console.print("Keine Messwerte in der Datenbank.")
        return

    console.print(build_average_table(all_average, readings))
    console.print(build_trend_table(readings))


def main():
    # forever show report
    while True:
        print_report()
        time.sleep(5)


if __name__ == "__main__":
    main()
