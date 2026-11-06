"""Explicit opt-in local history. Stores text summaries, never raw CVs or API keys."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = '''CREATE TABLE IF NOT EXISTS analyses (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 created_at TEXT NOT NULL,
 cv_ref TEXT NOT NULL,
 job_title TEXT NOT NULL,
 matched TEXT NOT NULL,
 missing TEXT NOT NULL,
 coverage REAL
)'''

def save_analysis(path, cv_ref, job_title, matched, missing, coverage):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute(SCHEMA)
        db.execute('INSERT INTO analyses (created_at,cv_ref,job_title,matched,missing,coverage) VALUES (?,?,?,?,?,?)',
            (datetime.now(timezone.utc).isoformat(timespec='seconds'),str(cv_ref)[:80],str(job_title)[:180],json.dumps(matched),json.dumps(missing),coverage))

def list_analyses(path, limit=50):
    if not Path(path).exists(): return []
    with sqlite3.connect(path) as db:
        db.execute(SCHEMA)
        rows=db.execute('SELECT created_at,cv_ref,job_title,matched,missing,coverage FROM analyses ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
    return [{'date':r[0],'cv_reference':r[1],'poste':r[2],'communes':', '.join(json.loads(r[3])), 'non_detectees':', '.join(json.loads(r[4])), 'couverture':r[5]} for r in rows]

def clear_analyses(path):
    if Path(path).exists():
        with sqlite3.connect(path) as db:
            db.execute('DELETE FROM analyses')
