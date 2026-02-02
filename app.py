from flask import Flask, render_template, jsonify, redirect, flash
from datetime import datetime
import sqlite3
from game_logic import (
    update_planet_production,
    metal_mine_upgrade_cost,
    start_metal_mine_construction,
    finalize_construction_if_finished,
    )

app = Flask(__name__)
app.secret_key = "dev-secret-key"

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

    metal_mine_cost = None
    remaining_seconds = None

    if planet:
         # 1️⃣ Si terminó construcción, aplícala
        planet = finalize_construction_if_finished(planet)

        # 2️⃣ Actualiza producción por tiempo
        planet = update_planet_production(planet)

        # 3️⃣ Calcular tiempo restante si hay construcción
        if planet["building_type"] and planet["building_end_time"]:
            end_time = datetime.fromisoformat(planet["building_end_time"])
            now = datetime.utcnow()
            remaining_seconds = int((end_time - now).total_seconds())
            if remaining_seconds < 0:
                remaining_seconds = 0

        # 4️⃣ Calcular costo del siguiente nivel
        metal_mine_cost = metal_mine_upgrade_cost(
            planet["metal_mine_level"]
        )

    return render_template(
        "index.html",
        planet=planet,
        metal_mine_cost=metal_mine_cost,
        remaining_seconds=remaining_seconds
    )


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

@app.route("/upgrade/metal-mine", methods=["POST"])
def upgrade_metal_mine_route():
    conn = get_db_connection()
    planet = conn.execute("SELECT * FROM planets LIMIT 1").fetchone()
    conn.close()

    if planet:
        success, message = start_metal_mine_construction(planet)
        flash(message)

    # Redirige de vuelta a la home
    return redirect("/")





if __name__ == "__main__":
    app.run(debug=True)


