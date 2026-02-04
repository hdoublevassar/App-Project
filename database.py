"""
Database module for Sleep Tracker application.
Uses SQLite for simple, portable local storage.
"""

import sqlite3
import os
from datetime import datetime, date
from pathlib import Path

# Database file location:
# - If SLEEP_TRACKER_DB environment variable is set, use that (for Linux installs)
# - Otherwise, create in the same folder as this script (for development/Windows)
if os.environ.get('SLEEP_TRACKER_DB'):
    DATABASE_PATH = Path(os.environ['SLEEP_TRACKER_DB'])
else:
    DATABASE_PATH = Path(__file__).parent / "sleep_tracker.db"


def get_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn


def init_database():
    """
    Create all necessary tables if they don't exist.
    Called once when the app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Main sleep entries table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sleep_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date DATE NOT NULL UNIQUE,
            bed_time TEXT,
            wake_time TEXT,
            
            -- Medications (stored as 0 or 1)
            med_melatonin INTEGER DEFAULT 0,
            med_weed INTEGER DEFAULT 0,
            med_cold_medicine INTEGER DEFAULT 0,
            med_benadryl INTEGER DEFAULT 0,
            
            -- Mood and feelings (1-10 scale)
            wake_feeling INTEGER,
            overall_mood INTEGER,
            
            -- Optional notes
            wake_feeling_notes TEXT,
            mood_notes TEXT,
            general_notes TEXT,
            
            -- Timestamps for record keeping
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Mood check-ins throughout the day (for future predictive features)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date DATE NOT NULL,
            check_time TEXT NOT NULL,
            mood_level INTEGER NOT NULL,
            energy_level INTEGER NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (entry_date) REFERENCES sleep_entries(entry_date)
        )
    """)
    
    conn.commit()
    conn.close()


# ----- Sleep Entry Functions -----

def save_sleep_entry(data):
    """
    Save or update a sleep entry for a specific date.
    If an entry already exists for that date, it updates it.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if entry exists for this date
    cursor.execute(
        "SELECT id FROM sleep_entries WHERE entry_date = ?", 
        (data['entry_date'],)
    )
    existing = cursor.fetchone()
    
    if existing:
        # Update existing entry
        cursor.execute("""
            UPDATE sleep_entries SET
                bed_time = ?,
                wake_time = ?,
                med_melatonin = ?,
                med_weed = ?,
                med_cold_medicine = ?,
                med_benadryl = ?,
                wake_feeling = ?,
                overall_mood = ?,
                wake_feeling_notes = ?,
                mood_notes = ?,
                general_notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE entry_date = ?
        """, (
            data.get('bed_time'),
            data.get('wake_time'),
            data.get('med_melatonin', 0),
            data.get('med_weed', 0),
            data.get('med_cold_medicine', 0),
            data.get('med_benadryl', 0),
            data.get('wake_feeling'),
            data.get('overall_mood'),
            data.get('wake_feeling_notes'),
            data.get('mood_notes'),
            data.get('general_notes'),
            data['entry_date']
        ))
    else:
        # Insert new entry
        cursor.execute("""
            INSERT INTO sleep_entries (
                entry_date, bed_time, wake_time,
                med_melatonin, med_weed, med_cold_medicine, med_benadryl,
                wake_feeling, overall_mood,
                wake_feeling_notes, mood_notes, general_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['entry_date'],
            data.get('bed_time'),
            data.get('wake_time'),
            data.get('med_melatonin', 0),
            data.get('med_weed', 0),
            data.get('med_cold_medicine', 0),
            data.get('med_benadryl', 0),
            data.get('wake_feeling'),
            data.get('overall_mood'),
            data.get('wake_feeling_notes'),
            data.get('mood_notes'),
            data.get('general_notes')
        ))
    
    conn.commit()
    conn.close()


def get_sleep_entry(entry_date):
    """Get a single sleep entry by date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM sleep_entries WHERE entry_date = ?", 
        (entry_date,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_sleep_entries(limit=None):
    """Get all sleep entries, most recent first."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM sleep_entries ORDER BY entry_date DESC"
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_entries_for_month(year, month):
    """Get all entries for a specific month (for calendar view)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Format: entries where date is in the given month
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"
    
    cursor.execute("""
        SELECT * FROM sleep_entries 
        WHERE entry_date >= ? AND entry_date < ?
        ORDER BY entry_date
    """, (start_date, end_date))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ----- Mood Check-in Functions -----

def save_mood_checkin(data):
    """Save a mood/energy check-in."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO mood_checkins (
            entry_date, check_time, mood_level, energy_level, notes
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        data['entry_date'],
        data['check_time'],
        data['mood_level'],
        data['energy_level'],
        data.get('notes')
    ))
    
    conn.commit()
    conn.close()


def get_mood_checkins(entry_date):
    """Get all mood check-ins for a specific date."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM mood_checkins 
        WHERE entry_date = ?
        ORDER BY check_time
    """, (entry_date,))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_recent_mood_checkins(days=7):
    """Get mood check-ins from the last N days."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM mood_checkins 
        WHERE entry_date >= date('now', ?)
        ORDER BY entry_date, check_time
    """, (f'-{days} days',))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_mood_checkin(checkin_id):
    """Delete a mood check-in by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mood_checkins WHERE id = ?", (checkin_id,))
    conn.commit()
    conn.close()
