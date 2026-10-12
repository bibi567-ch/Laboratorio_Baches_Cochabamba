import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("DATABASE_PATH", "reportes.db")

@contextmanager
def connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ubicacion TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            severidad TEXT NOT NULL,
            reportado_por TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'pendiente',
            reparado_por TEXT,
            observacion_reparacion TEXT,
            creado_en TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")

def create_report(data):
    with connection() as conn:
        cur = conn.execute(
            "INSERT INTO reportes (ubicacion, descripcion, severidad, reportado_por) VALUES (?, ?, ?, ?)",
            (data["ubicacion"], data["descripcion"], data["severidad"], data["reportado_por"])
        )
        return dict(conn.execute("SELECT * FROM reportes WHERE id=?", (cur.lastrowid,)).fetchone())

def get_report(report_id):
    with connection() as conn:
        row = conn.execute("SELECT * FROM reportes WHERE id=?", (report_id,)).fetchone()
        return dict(row) if row else None

def list_reports():
    with connection() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM reportes ORDER BY id DESC").fetchall()]

def mark_repaired(report_id, repaired_by, observation):
    with connection() as conn:
        cur = conn.execute(
            "UPDATE reportes SET estado='reparado', reparado_por=?, observacion_reparacion=? WHERE id=?",
            (repaired_by, observation, report_id)
        )
        if cur.rowcount == 0:
            return None
        return dict(conn.execute("SELECT * FROM reportes WHERE id=?", (report_id,)).fetchone())
