"""
Database management module for KrishiAI using SQLite.
Provides persistent storage for Farmer Profiles, Fields, Calendar Tasks,
Saved Schemes, and Impact tracking.
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from src.config import DB_PATH

def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Creates a database connection with foreign key support enabled."""
    target_path = db_path if db_path else DB_PATH
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: Optional[Path] = None) -> None:
    """Initializes tables and indexes if they do not already exist."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # 1. Farmer Profile Table (Stores local farmer profile)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farmer_profile (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        farmer_name TEXT NOT NULL,
        preferred_language TEXT DEFAULT 'en',
        state TEXT NOT NULL DEFAULT 'Tamil Nadu',
        district TEXT NOT NULL,
        village TEXT,
        primary_crop TEXT NOT NULL,
        total_land_acres REAL NOT NULL,
        land_arrangement TEXT NOT NULL,
        irrigation_type TEXT NOT NULL,
        current_season TEXT NOT NULL,
        soil_type TEXT,
        is_woman_farmer INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # 2. Fields Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fields (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        field_name TEXT NOT NULL,
        crop TEXT NOT NULL,
        variety TEXT,
        area_acres REAL NOT NULL,
        sowing_date TEXT NOT NULL,
        irrigation_type TEXT NOT NULL,
        soil_type TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # 3. Calendar Tasks Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        field_id INTEGER,
        crop TEXT NOT NULL,
        task_name TEXT NOT NULL,
        growth_stage TEXT NOT NULL,
        scheduled_date TEXT NOT NULL,
        is_completed INTEGER DEFAULT 0,
        is_custom INTEGER DEFAULT 0,
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE
    );
    """)

    # 4. Saved Schemes Tracking Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_schemes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_id TEXT NOT NULL UNIQUE,
        scheme_name TEXT NOT NULL,
        department TEXT,
        application_status TEXT DEFAULT 'Planned',
        documents_checklist TEXT,
        reminder_date TEXT,
        farmer_notes TEXT,
        saved_at TEXT NOT NULL
    );
    """)

    # 5. Advisory View Log (For Impact Tracking)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS advisory_views (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        advisory_id TEXT NOT NULL,
        crop TEXT NOT NULL,
        category TEXT NOT NULL,
        viewed_at TEXT NOT NULL
    );
    """)

    # 6. Farm Economics & Harvest Records (Farmer-entered records for impact)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS farm_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        field_id INTEGER,
        record_type TEXT NOT NULL, -- 'INPUT_COST', 'HARVEST_YIELD', 'MARKET_SALE'
        description TEXT NOT NULL,
        amount_inr REAL,
        quantity_kg REAL,
        record_date TEXT NOT NULL,
        FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE SET NULL
    );
    """)

    conn.commit()
    conn.close()

# ---------------- Farmer Profile CRUD ----------------

def save_or_update_profile(profile_data: Dict[str, Any], db_path: Optional[Path] = None) -> None:
    """Inserts or updates the singleton farmer profile."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()

    cursor.execute("SELECT id FROM farmer_profile WHERE id = 1;")
    exists = cursor.fetchone()

    if exists:
        cursor.execute("""
            UPDATE farmer_profile SET
                farmer_name = :farmer_name,
                preferred_language = :preferred_language,
                state = :state,
                district = :district,
                village = :village,
                primary_crop = :primary_crop,
                total_land_acres = :total_land_acres,
                land_arrangement = :land_arrangement,
                irrigation_type = :irrigation_type,
                current_season = :current_season,
                soil_type = :soil_type,
                is_woman_farmer = :is_woman_farmer,
                updated_at = :updated_at
            WHERE id = 1;
        """, {**profile_data, "updated_at": now_str})
    else:
        cursor.execute("""
            INSERT INTO farmer_profile (
                id, farmer_name, preferred_language, state, district, village,
                primary_crop, total_land_acres, land_arrangement, irrigation_type,
                current_season, soil_type, is_woman_farmer, created_at, updated_at
            ) VALUES (
                1, :farmer_name, :preferred_language, :state, :district, :village,
                :primary_crop, :total_land_acres, :land_arrangement, :irrigation_type,
                :current_season, :soil_type, :is_woman_farmer, :created_at, :updated_at
            );
        """, {**profile_data, "created_at": now_str, "updated_at": now_str})

    conn.commit()
    conn.close()

def get_farmer_profile(db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Fetches the farmer profile, or returns None if onboarding is pending."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farmer_profile WHERE id = 1;")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

# ---------------- Fields CRUD ----------------

def add_field(field_data: Dict[str, Any], db_path: Optional[Path] = None) -> int:
    """Adds a new agricultural field."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO fields (
            field_name, crop, variety, area_acres, sowing_date,
            irrigation_type, soil_type, notes, created_at, updated_at
        ) VALUES (
            :field_name, :crop, :variety, :area_acres, :sowing_date,
            :irrigation_type, :soil_type, :notes, :created_at, :updated_at
        );
    """, {**field_data, "created_at": now_str, "updated_at": now_str})
    field_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return field_id

def get_all_fields(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Returns all registered fields ordered by creation date."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fields ORDER BY id DESC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_field_by_id(field_id: int, db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Fetches a single field by ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM fields WHERE id = ?;", (field_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_field(field_id: int, field_data: Dict[str, Any], db_path: Optional[Path] = None) -> bool:
    """Updates an existing field."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute("""
        UPDATE fields SET
            field_name = :field_name,
            crop = :crop,
            variety = :variety,
            area_acres = :area_acres,
            sowing_date = :sowing_date,
            irrigation_type = :irrigation_type,
            soil_type = :soil_type,
            notes = :notes,
            updated_at = :updated_at
        WHERE id = :id;
    """, {**field_data, "id": field_id, "updated_at": now_str})
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def delete_field(field_id: int, db_path: Optional[Path] = None) -> bool:
    """Deletes a field and automatically cascades task removals."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fields WHERE id = ?;", (field_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

# ---------------- Calendar Tasks CRUD ----------------

def add_calendar_task(task_data: Dict[str, Any], db_path: Optional[Path] = None) -> int:
    """Adds a task or reminder for a field."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO calendar_tasks (
            field_id, crop, task_name, growth_stage, scheduled_date,
            is_completed, is_custom, notes, created_at
        ) VALUES (
            :field_id, :crop, :task_name, :growth_stage, :scheduled_date,
            :is_completed, :is_custom, :notes, :created_at
        );
    """, {
        "field_id": task_data.get("field_id"),
        "crop": task_data["crop"],
        "task_name": task_data["task_name"],
        "growth_stage": task_data.get("growth_stage", "General"),
        "scheduled_date": task_data["scheduled_date"],
        "is_completed": task_data.get("is_completed", 0),
        "is_custom": task_data.get("is_custom", 0),
        "notes": task_data.get("notes", ""),
        "created_at": now_str
    })
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_tasks_for_field(field_id: Optional[int] = None, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Returns calendar tasks for a specific field or across all fields."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    if field_id is not None:
        cursor.execute("SELECT * FROM calendar_tasks WHERE field_id = ? ORDER BY scheduled_date ASC;", (field_id,))
    else:
        cursor.execute("SELECT * FROM calendar_tasks ORDER BY scheduled_date ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def toggle_task_completion(task_id: int, is_completed: bool, db_path: Optional[Path] = None) -> bool:
    """Updates completion state of a task."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE calendar_tasks SET is_completed = ? WHERE id = ?;", (1 if is_completed else 0, task_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def delete_calendar_task(task_id: int, db_path: Optional[Path] = None) -> bool:
    """Deletes a calendar task."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calendar_tasks WHERE id = ?;", (task_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

# ---------------- Saved Schemes CRUD ----------------

def save_scheme(scheme_data: Dict[str, Any], db_path: Optional[Path] = None) -> bool:
    """Saves a government scheme for tracking."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    docs_json = json.dumps(scheme_data.get("documents_checklist", {}))
    cursor.execute("""
        INSERT OR REPLACE INTO saved_schemes (
            scheme_id, scheme_name, department, application_status,
            documents_checklist, reminder_date, farmer_notes, saved_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        scheme_data["scheme_id"],
        scheme_data["scheme_name"],
        scheme_data.get("department", ""),
        scheme_data.get("application_status", "Planned"),
        docs_json,
        scheme_data.get("reminder_date"),
        scheme_data.get("farmer_notes", ""),
        now_str
    ))
    conn.commit()
    conn.close()
    return True

def get_saved_schemes(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Returns all schemes saved by the farmer."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_schemes ORDER BY saved_at DESC;")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["documents_checklist"] = json.loads(d["documents_checklist"]) if d["documents_checklist"] else {}
        except Exception:
            d["documents_checklist"] = {}
        result.append(d)
    return result

def update_saved_scheme_status(scheme_id: str, status: str, notes: Optional[str] = None, checklist: Optional[Dict] = None, db_path: Optional[Path] = None) -> bool:
    """Updates farmer personal progress tracking on a scheme."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    if checklist is not None:
        cursor.execute("""
            UPDATE saved_schemes SET application_status = ?, farmer_notes = COALESCE(?, farmer_notes), documents_checklist = ?
            WHERE scheme_id = ?;
        """, (status, notes, json.dumps(checklist), scheme_id))
    else:
        cursor.execute("""
            UPDATE saved_schemes SET application_status = ?, farmer_notes = COALESCE(?, farmer_notes)
            WHERE scheme_id = ?;
        """, (status, notes, scheme_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

def remove_saved_scheme(scheme_id: str, db_path: Optional[Path] = None) -> bool:
    """Removes a saved scheme."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_schemes WHERE scheme_id = ?;", (scheme_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected

# ---------------- Advisory Log & Impact Records ----------------

def log_advisory_view(advisory_id: str, crop: str, category: str, db_path: Optional[Path] = None) -> None:
    """Logs advisory consultation for personal activity reporting."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO advisory_views (advisory_id, crop, category, viewed_at)
        VALUES (?, ?, ?, ?);
    """, (advisory_id, crop, category, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def add_farm_record(record: Dict[str, Any], db_path: Optional[Path] = None) -> int:
    """Records an input cost or harvest record."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO farm_records (
            field_id, record_type, description, amount_inr, quantity_kg, record_date
        ) VALUES (
            :field_id, :record_type, :description, :amount_inr, :quantity_kg, :record_date
        );
    """, record)
    rec_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rec_id

def get_farm_records(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Fetches all farm input and harvest records."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM farm_records ORDER BY record_date DESC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def clear_all_data(db_path: Optional[Path] = None) -> None:
    """Deletes all user data (Privacy & Data Deletion feature)."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM farm_records;")
    cursor.execute("DELETE FROM advisory_views;")
    cursor.execute("DELETE FROM saved_schemes;")
    cursor.execute("DELETE FROM calendar_tasks;")
    cursor.execute("DELETE FROM fields;")
    cursor.execute("DELETE FROM farmer_profile;")
    conn.commit()
    conn.close()
