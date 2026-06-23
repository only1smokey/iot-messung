# install rich linux: sudo apt install python3-rich
# run here in this folder: python auswertung.py

import sys
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

project_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_dir))

# use same db code like website
from db import get_readings

console = Console()


def average(rows, name):
    # make average
    if not rows:
        return "--"

    value = sum(row[name] for row in rows) / len(rows)
    return f"{value:.2f}"


def hour(row):
    # get hour from db time
    return datetime.fromisoformat(row["created_at"]).hour


def rows_between(readings, start, end):
    # get rows from clock time
    return [row for row in readings if start <= hour(row) < end]


def add_row(table, name, rows):
    # add one table row
    table.add_row(
        name,
        str(len(rows)),
        average(rows, "temperature"),
        average(rows, "humidity"),
        average(rows, "pressure"),
    )


def show_report():
    # get db data
    readings = get_readings(200)

    console.clear()
    table = Table(title="Auswertung")
    table.add_column("Bereich")
    table.add_column("Anzahl")
    table.add_column("Temperatur C")
    table.add_column("Feuchtigkeit %")
    table.add_column("Luftdruck hPa")

    add_row(table, "Alle geladen", readings)
    add_row(table, "Letzte 5 Eintraege", readings[-5:])
    add_row(table, "Letzte 10 Eintraege", readings[-10:])

    add_row(table, "Nacht 00-06", rows_between(readings, 0, 6))
    add_row(table, "Morgen 06-12", rows_between(readings, 6, 12))
    add_row(table, "Mittag 12-18", rows_between(readings, 12, 18))
    add_row(table, "Abend 18-24", rows_between(readings, 18, 24))

    console.print(table)


def main():
    # forever show table
    while True:
        show_report()
        time.sleep(5)


if __name__ == "__main__":
    main()
