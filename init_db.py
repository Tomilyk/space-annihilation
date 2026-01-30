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
    last_update TEXT NOT NULL
)
""")

now = datetime.utcnow().isoformat()

conn.execute("""
INSERT INTO planets (name, metal, metal_production, last_update)
VALUES (?, ?, ?, ?)
""", ("Tierra", 500, 30, now))

conn.commit()
conn.close()

print("Base de datos inicializada con producción.")
