import os
from pathlib import Path

from dotenv import load_dotenv
from mysql.connector import connect

# env file here
load_dotenv(Path(__file__).resolve().with_name(".env"))

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "nodered")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "iot_db")
DB_TABLE = os.getenv("DB_TABLE", "sensor_data")


def connect_db():
    # db open
    return connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        connection_timeout=5,
    )


def number(value):
    # make number nice
    return round(float(value), 2)


def get_readings(limit=60):
    # get last sensor stuff
    connection = connect_db()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            f"""
            SELECT id, temperature, humidity, pressure, created_at
            FROM `{DB_TABLE}`
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        )

        rows = list(reversed(cursor.fetchall()))

        return [
            {
                "id": int(row["id"]),
                "temperature": number(row["temperature"]),
                "humidity": number(row["humidity"]),
                "pressure": number(row["pressure"]),
                "created_at": row["created_at"].isoformat(timespec="seconds"),
            }
            for row in rows
        ]
    finally:
        cursor.close()
        connection.close()


def get_averages():
    # get average sensor stuff
    connection = connect_db()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            f"""
            SELECT
                COUNT(*) AS count,
                AVG(temperature) AS temperature,
                AVG(humidity) AS humidity,
                AVG(pressure) AS pressure
            FROM `{DB_TABLE}`
            """
        )

        row = cursor.fetchone()

        if not row or row["count"] == 0:
            return None

        return {
            "count": int(row["count"]),
            "temperature": number(row["temperature"]),
            "humidity": number(row["humidity"]),
            "pressure": number(row["pressure"]),
        }
    finally:
        cursor.close()
        connection.close()


def clear_database():
    # delete all sensor stuff
    connection = connect_db()
    cursor = connection.cursor()

    try:
        cursor.execute(f"DELETE FROM `{DB_TABLE}`")
        deleted = cursor.rowcount
        connection.commit()
        return deleted
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
