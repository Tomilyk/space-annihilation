from datetime import datetime, timedelta
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

def metal_mine_upgrade_cost(level):
    """
    Calcula el costo en metal para subir la mina
    del nivel actual al siguiente.
    """
    base_cost = 50
    multiplier = 2

    return int(base_cost * (multiplier ** (level - 1)))


def metal_mine_production(level):
    """
    Calcula la producción TOTAL de metal por hora
    según el nivel de la mina.
    """
    base_production = 60  # producción nivel 1
    production_per_level = 2 * base_production 

    return base_production + (level - 1) * production_per_level

def upgrade_metal_mine(planet):
    """
    Intenta subir el nivel de la mina de metal.
    Devuelve (success, message).
    """
    current_level = planet["metal_mine_level"]
    cost = metal_mine_upgrade_cost(current_level)

    # Validar recursos
    if planet["metal"] < cost:
        return False, "No tienes suficiente metal."

    new_level = current_level + 1
    new_metal = planet["metal"] - cost
    new_production = metal_mine_production(new_level)

    conn = get_db_connection()
    conn.execute("""
        UPDATE planets
        SET metal = ?,
            metal_mine_level = ?,
            metal_production = ?
        WHERE id = ?
    """, (new_metal, new_level, new_production, planet["id"]))
    conn.commit()
    conn.close()

    return True, f"Mina de metal subida a nivel {new_level}."

def metal_mine_build_time(level):
    """
    Devuelve el tiempo de construcción en segundos
    para subir la mina desde el nivel actual.
    """
    base_time = 3  # segundos
    return base_time * (level + 1)

def start_metal_mine_construction(planet):
    """
    Inicia la construcción de la mina de metal.
    NO sube el nivel todavía.
    """
    # Ya hay construcción en progreso
    if planet["building_type"] is not None:
        return False, "Ya hay una construcción en progreso."

    current_level = planet["metal_mine_level"]
    cost = metal_mine_upgrade_cost(current_level)

    # Validar metal suficiente
    if planet["metal"] < cost:
        return False, "No tienes suficiente metal."

    # Calcular tiempo
    build_seconds = metal_mine_build_time(current_level)
    end_time = datetime.utcnow() + timedelta(seconds=build_seconds)

    # Descontar metal e iniciar construcción
    conn = get_db_connection()
    conn.execute("""
        UPDATE planets
        SET metal = ?,
            building_type = ?,
            building_end_time = ?
        WHERE id = ?
    """, (
        planet["metal"] - cost,
        "metal_mine",
        end_time.isoformat(),
        planet["id"]
    ))
    conn.commit()
    conn.close()

    return True, "Construcción iniciada."

def finalize_construction_if_finished(planet):
    """
    Si hay una construcción y ya terminó, aplica el upgrade
    y limpia el estado de construcción.
    """
    if planet["building_type"] is None:
        return planet

    end_time = datetime.fromisoformat(planet["building_end_time"])
    now = datetime.utcnow()

    # Aún no termina
    if now < end_time:
        return planet

    # Terminó: aplicar efectos
    if planet["building_type"] == "metal_mine":
        new_level = planet["metal_mine_level"] + 1
        new_production = metal_mine_production(new_level)

        conn = get_db_connection()
        conn.execute("""
            UPDATE planets
            SET metal_mine_level = ?,
                metal_production = ?,
                building_type = NULL,
                building_end_time = NULL
            WHERE id = ?
        """, (
            new_level,
            new_production,
            planet["id"]
        ))
        conn.commit()
        conn.close()

        # Actualizar objeto en memoria
        planet = dict(planet)
        planet["metal_mine_level"] = new_level
        planet["metal_production"] = new_production
        planet["building_type"] = None
        planet["building_end_time"] = None

    return planet