# run: python simple_manual_script\auswertung.py

import sys
import time
from pathlib import Path

project_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_dir))

# use same db code like website
from db import get_averages


def print_averages():
    # ask db for average
    averages = get_averages()

    if not averages:
        print("Keine Messwerte in der Datenbank.")
        return

    print(
        f"{averages['count']} Messwerte | "
        f"Temperatur: {averages['temperature']:.2f} C | "
        f"Feuchtigkeit: {averages['humidity']:.2f} % | "
        f"Luftdruck: {averages['pressure']:.2f} hPa"
    )


def main():
    print("Auswertung laeuft. Beenden mit STRG+C.")

    # forever print average
    while True:
        print_averages()
        time.sleep(5)


if __name__ == "__main__":
    main()
