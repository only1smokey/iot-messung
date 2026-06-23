from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from db import clear_database, get_averages, get_readings

app = Flask(__name__)
base_dir = Path(__file__).resolve().parent


@app.get("/")
def index():
    # show website
    return send_from_directory(base_dir, "index.html")


@app.get("/style.css")
def style():
    return send_from_directory(base_dir, "style.css")


@app.get("/script.js")
def script():
    return send_from_directory(base_dir, "script.js")


@app.get("/api/readings")
def readings():
    # website ask data here
    try:
        data = get_readings()
        return jsonify(
            ok=True,
            averages=get_averages(),
            latest=data[-1] if data else None,
            readings=data,
        )
    except Exception as error:
        return jsonify(ok=False, error=str(error)), 500


@app.post("/api/clear")
def clear():
    # clear button use this
    try:
        deleted = clear_database()
        return jsonify(ok=True, deleted=deleted)
    except Exception as error:
        return jsonify(ok=False, error=str(error)), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
