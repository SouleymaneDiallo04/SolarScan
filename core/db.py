"""Couche base de données (SQLite).

Schéma volontairement compatible avec une migration **PostgreSQL + PostGIS**
(les colonnes lat/lon deviendront une géométrie POINT). Persistance réelle des
inspections, panneaux, sévérités et statuts de maintenance.
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / 'solarscan.db'

SCHEMA = """
CREATE TABLE IF NOT EXISTS inspections (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  nom           TEXT,
  date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
  n_panneaux    INTEGER,
  n_anomalies   INTEGER
);
CREATE TABLE IF NOT EXISTS panels (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  inspection_id INTEGER REFERENCES inspections(id),
  source        TEXT,
  lat           REAL,
  lon           REAL,
  classe        TEXT,
  confiance     REAL,
  anomalie      INTEGER,
  severite      TEXT,
  rang          INTEGER,
  perte_pct     REAL,
  perte_kwh_an  REAL,
  perte_eur_an  REAL,
  statut        TEXT DEFAULT 'a_valider'
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def create_inspection(nom, panels):
    conn = get_conn()
    cur = conn.cursor()
    n_anom = sum(p['anomalie'] for p in panels)
    cur.execute('INSERT INTO inspections(nom, n_panneaux, n_anomalies) VALUES (?,?,?)',
                (nom, len(panels), n_anom))
    iid = cur.lastrowid
    for p in panels:
        cur.execute(
            """INSERT INTO panels(inspection_id, source, lat, lon, classe, confiance,
                 anomalie, severite, rang, perte_pct, perte_kwh_an, perte_eur_an, statut)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (iid, p['source'], p['lat'], p['lon'], p['classe'], p['confiance'],
             p['anomalie'], p['severite'], p['rang'], p['perte_pct'],
             p['perte_kwh_an'], p['perte_eur_an'], 'a_valider'))
    conn.commit()
    conn.close()
    return iid


def list_inspections():
    conn = get_conn()
    rows = conn.execute('SELECT * FROM inspections ORDER BY id DESC').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_panels(inspection_id, only_anomalies=False):
    conn = get_conn()
    q = 'SELECT * FROM panels WHERE inspection_id=?'
    if only_anomalies:
        q += ' AND anomalie=1'
    q += ' ORDER BY rang DESC, perte_eur_an DESC'
    rows = conn.execute(q, (inspection_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_status(panel_id, statut):
    conn = get_conn()
    conn.execute('UPDATE panels SET statut=? WHERE id=?', (statut, panel_id))
    conn.commit()
    conn.close()
