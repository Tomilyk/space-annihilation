from flask import Flask, render_template, jsonify
import sqlite3
from game_logic import update_planet_production

app = Flask(__name__)
DATABASE = "spaceannihilation.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    conn = get_db_connection()
    planet = conn.execute("SELECT * FROM planets LIMIT 1").fetchone()
    conn.close()

    if planet:
        planet = update_planet_production(planet)

    return render_template("index.html", planet=planet)


# 👉 NUEVO: endpoint API
@app.route("/api/planet")
def planet_api():
    conn = get_db_connection()
    planet = conn.execute("SELECT * FROM planets LIMIT 1").fetchone()
    conn.close()

    if planet:
        planet = update_planet_production(planet)

        return jsonify({
            "id": planet["id"],
            "name": planet["name"],
            "metal": planet["metal"],
            "metal_production": planet["metal_production"],
            "last_update": planet["last_update"]
        })

    return jsonify({"error": "No planet found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
