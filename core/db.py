"""Couche base de données (SQLAlchemy) — agnostique.

- En local : SQLite (`solarscan.db`), zéro config.
- En production : PostgreSQL / PostGIS via la variable d'env `DATABASE_URL`
  (ex. postgresql+psycopg2://user:pass@db:5432/solarscan).

Le même code marche dans les deux cas → déployable d'un coup avec docker-compose.
"""
import os
from pathlib import Path

from sqlalchemy import (create_engine, MetaData, Table, Column, Integer, String,
                        Float, DateTime, ForeignKey, func, select, insert, update, desc)

ROOT = Path(__file__).resolve().parent.parent
DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{ROOT / "solarscan.db"}')
engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

inspections = Table(
    'inspections', metadata,
    Column('id', Integer, primary_key=True),
    Column('nom', String),
    Column('date_creation', DateTime, server_default=func.now()),
    Column('n_panneaux', Integer),
    Column('n_anomalies', Integer),
)

panels = Table(
    'panels', metadata,
    Column('id', Integer, primary_key=True),
    Column('inspection_id', Integer, ForeignKey('inspections.id')),
    Column('source', String),
    Column('lat', Float),
    Column('lon', Float),
    Column('classe', String),
    Column('confiance', Float),
    Column('anomalie', Integer),
    Column('severite', String),
    Column('rang', Integer),
    Column('perte_pct', Float),
    Column('perte_kwh_an', Float),
    Column('perte_eur_an', Float),
    Column('statut', String, default='a_valider'),
)


def init_db():
    metadata.create_all(engine)


def create_inspection(nom, panels_data):
    n_anom = sum(p['anomalie'] for p in panels_data)
    with engine.begin() as conn:
        res = conn.execute(insert(inspections).values(
            nom=nom, n_panneaux=len(panels_data), n_anomalies=n_anom))
        iid = res.inserted_primary_key[0]
        if panels_data:
            conn.execute(insert(panels), [
                {**p, 'inspection_id': iid, 'statut': 'a_valider'} for p in panels_data])
    return iid


def list_inspections():
    with engine.connect() as conn:
        rows = conn.execute(select(inspections).order_by(desc(inspections.c.id))).mappings().all()
    return [dict(r) for r in rows]


def get_panels(inspection_id, only_anomalies=False):
    q = select(panels).where(panels.c.inspection_id == inspection_id)
    if only_anomalies:
        q = q.where(panels.c.anomalie == 1)
    q = q.order_by(desc(panels.c.rang), desc(panels.c.perte_eur_an))
    with engine.connect() as conn:
        rows = conn.execute(q).mappings().all()
    return [dict(r) for r in rows]


def update_status(panel_id, statut):
    with engine.begin() as conn:
        conn.execute(update(panels).where(panels.c.id == panel_id).values(statut=statut))
