from datetime import datetime
import sqlite3

DATABASE = "spaceannihilation.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def update_planet_production(planet):
    """
    Calcula el metal producido desde la última actualización
    y actualiza la base de datos.
    """
    last_update = datetime.fromisoformat(planet["last_update"])
    now = datetime.utcnow()

    seconds_passed = (now - last_update).total_seconds()
    hours_passed = seconds_passed / 3600

    produced_metal = int(hours_passed * planet["metal_production"])

    if produced_metal > 0:
        new_metal = planet["metal"] + produced_metal

        conn = get_db_connection()
        conn.execute("""
            UPDATE planets
            SET metal = ?, last_update = ?
            WHERE id = ?
        """, (new_metal, now.isoformat(), planet["id"]))
        conn.commit()
        conn.close()

        planet = dict(planet)
        planet["metal"] = new_metal
        planet["last_update"] = now.isoformat()

    return planet
