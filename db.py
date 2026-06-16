import os

from dotenv import load_dotenv
from mysql.connector import pooling

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "nodered")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "iot_db")
DB_TABLE = os.getenv("DB_TABLE", "sensor_data")

pool = pooling.MySQLConnectionPool(
    pool_name="sensor_pool",
    pool_size=5,
    pool_reset_session=True,
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    connection_timeout=5,
)


def get_readings(limit=60):
    connection = pool.get_connection()
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
                "temperature": round(float(row["temperature"]), 2),
                "humidity": round(float(row["humidity"]), 2),
                "pressure": round(float(row["pressure"]), 2),
                "created_at": row["created_at"].isoformat(timespec="seconds"),
            }
            for row in rows
        ]
    finally:
        cursor.close()
        connection.close()


def clear_database():
    connection = pool.get_connection()
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
