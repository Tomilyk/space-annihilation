import sqlite3
from datetime import datetime

conn = sqlite3.connect("spaceannihilation.db")

conn.execute("DROP TABLE IF EXISTS planets")

conn.execute("""
CREATE TABLE planets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    metal INTEGER NOT NULL,
    metal_production INTEGER NOT NULL,
    metal_mine_level INTEGER NOT NULL,
    building_type TEXT,
    building_end_time TEXT,
    last_update TEXT NOT NULL
)
""")

now = datetime.utcnow().isoformat()

conn.execute("""
INSERT INTO planets (
    name,
    metal,
    metal_production,
    metal_mine_level,
    building_type,
    building_end_time,
    last_update
)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    "Tierra",
    1000,
    60,
    0,
    None,
    None,
    now
))

conn.commit()
conn.close()

print("Base de datos inicializada con tiempo de construcción.")