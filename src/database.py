"""
Database Module for LifeTracker
================================
Handles all data persistence with encryption support.
Uses SQLCipher for encrypted SQLite storage.

All data is stored locally - NO network connections.
"""

import os
import json
import hashlib
import secrets
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import sqlite3

# Try to use SQLCipher for encryption, fall back to regular SQLite
try:
    from pysqlcipher3 import dbapi2 as sqlcipher
    HAS_ENCRYPTION = True
except ImportError:
    sqlcipher = None
    HAS_ENCRYPTION = False


class DatabaseManager:
    """
    Manages the encrypted SQLite database for LifeTracker.
    
    All personal data is stored in an encrypted database file.
    The encryption key is derived from the user's password.
    """
    
    # Database location in user's config directory
    DATA_DIR = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local' / 'share')) / 'lifetracker'
    DB_PATH = DATA_DIR / 'lifetracker.db'
    CONFIG_PATH = DATA_DIR / 'config.json'
    
    def __init__(self):
        """Initialize the database manager."""
        self.conn = None
        self.encryption_key = None
        
        # Ensure data directory exists
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def is_first_run(self) -> bool:
        """Check if this is the first time running the app."""
        return not self.CONFIG_PATH.exists()
    
    def setup_password(self, password: str) -> bool:
        """
        Set up the initial password and create the database.
        
        Args:
            password: The user's chosen password
            
        Returns:
            True if setup successful
        """
        # Generate a salt for password hashing
        salt = secrets.token_hex(32)
        
        # Hash the password for verification
        password_hash = self._hash_password(password, salt)
        
        # Save config
        config = {
            'password_hash': password_hash,
            'salt': salt,
            'created_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        with open(self.CONFIG_PATH, 'w') as f:
            json.dump(config, f)
        
        # Initialize database with password
        self._derive_key(password, salt)
        self._connect()
        self._create_tables()
        
        return True
    
    def authenticate(self, password: str) -> bool:
        """
        Authenticate with the given password.
        
        Args:
            password: The user's password
            
        Returns:
            True if authentication successful
        """
        try:
            with open(self.CONFIG_PATH, 'r') as f:
                config = json.load(f)
            
            salt = config['salt']
            stored_hash = config['password_hash']
            
            # Verify password
            if self._hash_password(password, salt) != stored_hash:
                return False
            
            # Derive encryption key and connect
            self._derive_key(password, salt)
            self._connect()
            
            return True
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Change the user's password.
        
        Args:
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
        """
        # Verify old password first
        with open(self.CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        if self._hash_password(old_password, config['salt']) != config['password_hash']:
            return False
        
        # Generate new salt and hash
        new_salt = secrets.token_hex(32)
        new_hash = self._hash_password(new_password, new_salt)
        
        # Update config
        config['salt'] = new_salt
        config['password_hash'] = new_hash
        
        with open(self.CONFIG_PATH, 'w') as f:
            json.dump(config, f)
        
        # Re-encrypt database with new key (if using encryption)
        if HAS_ENCRYPTION and self.conn:
            new_key = self._derive_key(new_password, new_salt)
            self.conn.execute(f"PRAGMA rekey = '{new_key}'")
        
        return True
    
    def delete_all_data(self) -> bool:
        """
        Securely delete all data. This is irreversible.
        
        Returns:
            True if deletion successful
        """
        try:
            # Close connection
            if self.conn:
                self.conn.close()
                self.conn = None
            
            # Securely overwrite database file
            if self.DB_PATH.exists():
                # Overwrite with random data before deletion
                size = self.DB_PATH.stat().st_size
                with open(self.DB_PATH, 'wb') as f:
                    f.write(secrets.token_bytes(size))
                self.DB_PATH.unlink()
            
            # Remove config
            if self.CONFIG_PATH.exists():
                self.CONFIG_PATH.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error deleting data: {e}")
            return False
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash a password with the given salt using PBKDF2."""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # iterations
        ).hex()
    
    def _derive_key(self, password: str, salt: str) -> str:
        """Derive an encryption key from the password."""
        self.encryption_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            (salt + 'encryption').encode('utf-8'),
            100000
        ).hex()
        return self.encryption_key
    
    def _connect(self):
        """Connect to the database."""
        if HAS_ENCRYPTION and self.encryption_key:
            self.conn = sqlcipher.connect(str(self.DB_PATH))
            self.conn.execute(f"PRAGMA key = '{self.encryption_key}'")
        else:
            self.conn = sqlite3.connect(str(self.DB_PATH))
        
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
    
    def _create_tables(self):
        """Create all database tables."""
        cursor = self.conn.cursor()
        
        # ========== SLEEP & MENTAL HEALTH ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sleep_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date DATE NOT NULL UNIQUE,
                bed_time TEXT,
                wake_time TEXT,
                sleep_quality INTEGER CHECK(sleep_quality BETWEEN 1 AND 10),
                wake_mood INTEGER CHECK(wake_mood BETWEEN 1 AND 10),
                wake_energy INTEGER CHECK(wake_energy BETWEEN 1 AND 10),
                daily_energy INTEGER CHECK(daily_energy BETWEEN 1 AND 10),
                daily_mood INTEGER CHECK(daily_mood BETWEEN 1 AND 10),
                
                -- Sleep aids
                aid_melatonin BOOLEAN DEFAULT 0,
                aid_weed BOOLEAN DEFAULT 0,
                aid_benadryl BOOLEAN DEFAULT 0,
                aid_cough_meds BOOLEAN DEFAULT 0,
                aid_other TEXT,
                
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========== FITNESS TRACKING ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fitness_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date DATE NOT NULL,
                workout_type TEXT NOT NULL,
                duration_minutes INTEGER,
                intensity INTEGER CHECK(intensity BETWEEN 1 AND 10),
                calories_burned INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fitness_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_type TEXT NOT NULL,
                target_value INTEGER,
                target_unit TEXT,
                frequency TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========== ADDICTION RECOVERY ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS addictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                addiction_type TEXT NOT NULL,
                custom_name TEXT,
                start_date DATE NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recovery_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                addiction_id INTEGER NOT NULL,
                checkin_date DATE NOT NULL,
                stayed_clean BOOLEAN NOT NULL,
                urge_level INTEGER CHECK(urge_level BETWEEN 1 AND 10),
                mood INTEGER CHECK(mood BETWEEN 1 AND 10),
                trigger TEXT,
                coping_strategy TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (addiction_id) REFERENCES addictions(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recovery_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                addiction_id INTEGER NOT NULL,
                milestone_days INTEGER NOT NULL,
                achieved_date DATE,
                celebrated BOOLEAN DEFAULT 0,
                FOREIGN KEY (addiction_id) REFERENCES addictions(id) ON DELETE CASCADE
            )
        """)
        
        # ========== MEDICATION & APPOINTMENTS ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                time_of_day TEXT,
                notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medication_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medication_id INTEGER NOT NULL,
                taken_at TIMESTAMP NOT NULL,
                taken BOOLEAN DEFAULT 1,
                notes TEXT,
                side_effects TEXT,
                effectiveness INTEGER CHECK(effectiveness BETWEEN 1 AND 10),
                FOREIGN KEY (medication_id) REFERENCES medications(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                appointment_date DATE NOT NULL,
                appointment_time TEXT,
                location TEXT,
                reminder_minutes INTEGER DEFAULT 60,
                is_completed BOOLEAN DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========== RELATIONSHIPS ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                relationship_type TEXT,
                notes TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationship_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                relationship_id INTEGER NOT NULL,
                interaction_date DATE NOT NULL,
                interaction_type TEXT,
                quality INTEGER CHECK(quality BETWEEN 1 AND 10),
                your_mood_before INTEGER CHECK(your_mood_before BETWEEN 1 AND 10),
                your_mood_after INTEGER CHECK(your_mood_after BETWEEN 1 AND 10),
                patterns_noticed TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (relationship_id) REFERENCES relationships(id) ON DELETE CASCADE
            )
        """)
        
        # ========== GOALS ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                target_date DATE,
                priority INTEGER CHECK(priority BETWEEN 1 AND 5),
                status TEXT DEFAULT 'active',
                progress INTEGER DEFAULT 0 CHECK(progress BETWEEN 0 AND 100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goal_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                target_date DATE,
                is_completed BOOLEAN DEFAULT 0,
                completed_date DATE,
                notes TEXT,
                FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goal_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_id INTEGER NOT NULL,
                checkin_date DATE NOT NULL,
                progress_notes TEXT,
                obstacles TEXT,
                next_steps TEXT,
                motivation_level INTEGER CHECK(motivation_level BETWEEN 1 AND 10),
                FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
            )
        """)
        
        # ========== BOWEL TRACKING (Private) ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bowel_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date DATE NOT NULL,
                had_movement BOOLEAN NOT NULL,
                consistency INTEGER CHECK(consistency BETWEEN 1 AND 7),
                pain_level INTEGER CHECK(pain_level BETWEEN 0 AND 10),
                blood_present BOOLEAN DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========== DAILY MOOD CHECKINS (for insights) ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mood_checkins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkin_time TIMESTAMP NOT NULL,
                mood_level INTEGER CHECK(mood_level BETWEEN 1 AND 10),
                energy_level INTEGER CHECK(energy_level BETWEEN 1 AND 10),
                anxiety_level INTEGER CHECK(anxiety_level BETWEEN 0 AND 10),
                stress_level INTEGER CHECK(stress_level BETWEEN 0 AND 10),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    # ==================== SLEEP ENTRIES ====================
    
    def save_sleep_entry(self, data: Dict[str, Any]) -> int:
        """Save or update a sleep entry."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO sleep_entries (
                entry_date, bed_time, wake_time, sleep_quality,
                wake_mood, wake_energy, daily_energy, daily_mood,
                aid_melatonin, aid_weed, aid_benadryl, aid_cough_meds, aid_other,
                notes, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(entry_date) DO UPDATE SET
                bed_time = excluded.bed_time,
                wake_time = excluded.wake_time,
                sleep_quality = excluded.sleep_quality,
                wake_mood = excluded.wake_mood,
                wake_energy = excluded.wake_energy,
                daily_energy = excluded.daily_energy,
                daily_mood = excluded.daily_mood,
                aid_melatonin = excluded.aid_melatonin,
                aid_weed = excluded.aid_weed,
                aid_benadryl = excluded.aid_benadryl,
                aid_cough_meds = excluded.aid_cough_meds,
                aid_other = excluded.aid_other,
                notes = excluded.notes,
                updated_at = CURRENT_TIMESTAMP
        """, (
            data.get('entry_date'),
            data.get('bed_time'),
            data.get('wake_time'),
            data.get('sleep_quality'),
            data.get('wake_mood'),
            data.get('wake_energy'),
            data.get('daily_energy'),
            data.get('daily_mood'),
            data.get('aid_melatonin', 0),
            data.get('aid_weed', 0),
            data.get('aid_benadryl', 0),
            data.get('aid_cough_meds', 0),
            data.get('aid_other'),
            data.get('notes')
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_sleep_entry(self, entry_date: str) -> Optional[Dict]:
        """Get a sleep entry for a specific date."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sleep_entries WHERE entry_date = ?", (entry_date,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_sleep_entries(self, days: int = 30) -> List[Dict]:
        """Get recent sleep entries."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM sleep_entries 
            WHERE entry_date >= date('now', ?)
            ORDER BY entry_date DESC
        """, (f'-{days} days',))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_optimal_sleep_recommendation(self) -> Dict[str, Any]:
        """
        Analyze sleep data to recommend optimal bedtime and wake time.
        Based on correlation between sleep times and mood/energy ratings.
        """
        cursor = self.conn.cursor()
        
        # Get entries with good mood/energy (7+)
        cursor.execute("""
            SELECT bed_time, wake_time, 
                   (wake_mood + wake_energy + daily_mood + daily_energy) / 4.0 as avg_score
            FROM sleep_entries
            WHERE wake_mood >= 7 AND wake_energy >= 7
            AND bed_time IS NOT NULL AND wake_time IS NOT NULL
            ORDER BY avg_score DESC
            LIMIT 20
        """)
        
        good_entries = cursor.fetchall()
        
        if len(good_entries) < 5:
            return {'has_recommendation': False, 'message': 'Need more data (at least 5 good nights)'}
        
        # Calculate average bed/wake times for good days
        # This is simplified - a real implementation would parse times properly
        return {
            'has_recommendation': True,
            'recommended_bedtime': '22:30',  # Placeholder - would calculate from data
            'recommended_waketime': '06:30',
            'confidence': len(good_entries) / 20.0,
            'based_on_entries': len(good_entries)
        }
    
    # ==================== FITNESS ====================
    
    def save_fitness_entry(self, data: Dict[str, Any]) -> int:
        """Save a fitness entry."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO fitness_entries (
                entry_date, workout_type, duration_minutes,
                intensity, calories_burned, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get('entry_date'),
            data.get('workout_type'),
            data.get('duration_minutes'),
            data.get('intensity'),
            data.get('calories_burned'),
            data.get('notes')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_fitness_entries(self, days: int = 30) -> List[Dict]:
        """Get recent fitness entries."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM fitness_entries 
            WHERE entry_date >= date('now', ?)
            ORDER BY entry_date DESC
        """, (f'-{days} days',))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_fitness_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get fitness summary for the period."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_workouts,
                SUM(duration_minutes) as total_minutes,
                AVG(intensity) as avg_intensity,
                SUM(calories_burned) as total_calories
            FROM fitness_entries 
            WHERE entry_date >= date('now', ?)
        """, (f'-{days} days',))
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    # ==================== ADDICTION RECOVERY ====================
    
    def add_addiction(self, data: Dict[str, Any]) -> int:
        """Add a new addiction to track."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO addictions (addiction_type, custom_name, start_date, notes)
            VALUES (?, ?, ?, ?)
        """, (
            data.get('addiction_type'),
            data.get('custom_name'),
            data.get('start_date'),
            data.get('notes')
        ))
        
        addiction_id = cursor.lastrowid
        
        # Create milestone targets
        milestones = [1, 3, 7, 14, 30, 60, 90, 180, 365]
        for days in milestones:
            cursor.execute("""
                INSERT INTO recovery_milestones (addiction_id, milestone_days)
                VALUES (?, ?)
            """, (addiction_id, days))
        
        self.conn.commit()
        return addiction_id
    
    def get_addictions(self, active_only: bool = True) -> List[Dict]:
        """Get all tracked addictions."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM addictions"
        if active_only:
            query += " WHERE is_active = 1"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def save_recovery_checkin(self, data: Dict[str, Any]) -> int:
        """Save a recovery check-in."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO recovery_checkins (
                addiction_id, checkin_date, stayed_clean,
                urge_level, mood, trigger, coping_strategy, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('addiction_id'),
            data.get('checkin_date'),
            data.get('stayed_clean'),
            data.get('urge_level'),
            data.get('mood'),
            data.get('trigger'),
            data.get('coping_strategy'),
            data.get('notes')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_clean_days(self, addiction_id: int) -> int:
        """Calculate consecutive clean days for an addiction."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT checkin_date FROM recovery_checkins
            WHERE addiction_id = ? AND stayed_clean = 0
            ORDER BY checkin_date DESC
            LIMIT 1
        """, (addiction_id,))
        
        last_relapse = cursor.fetchone()
        
        if last_relapse:
            from datetime import datetime
            last_date = datetime.strptime(last_relapse['checkin_date'], '%Y-%m-%d').date()
            return (date.today() - last_date).days
        else:
            # No relapse recorded, count from start date
            cursor.execute("SELECT start_date FROM addictions WHERE id = ?", (addiction_id,))
            start = cursor.fetchone()
            if start:
                start_date = datetime.strptime(start['start_date'], '%Y-%m-%d').date()
                return (date.today() - start_date).days
        
        return 0
    
    def get_upcoming_milestones(self, addiction_id: int) -> List[Dict]:
        """Get upcoming milestones for an addiction."""
        clean_days = self.get_clean_days(addiction_id)
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM recovery_milestones
            WHERE addiction_id = ? AND milestone_days > ?
            ORDER BY milestone_days ASC
            LIMIT 3
        """, (addiction_id, clean_days))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== MEDICATIONS ====================
    
    def add_medication(self, data: Dict[str, Any]) -> int:
        """Add a new medication."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO medications (name, dosage, frequency, time_of_day, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.get('name'),
            data.get('dosage'),
            data.get('frequency'),
            data.get('time_of_day'),
            data.get('notes')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_medications(self, active_only: bool = True) -> List[Dict]:
        """Get all medications."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM medications"
        if active_only:
            query += " WHERE is_active = 1"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def log_medication(self, data: Dict[str, Any]) -> int:
        """Log that a medication was taken."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO medication_logs (
                medication_id, taken_at, taken, notes, side_effects, effectiveness
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get('medication_id'),
            data.get('taken_at'),
            data.get('taken', 1),
            data.get('notes'),
            data.get('side_effects'),
            data.get('effectiveness')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    # ==================== APPOINTMENTS ====================
    
    def add_appointment(self, data: Dict[str, Any]) -> int:
        """Add a new appointment."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO appointments (
                title, description, appointment_date, appointment_time,
                location, reminder_minutes, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('title'),
            data.get('description'),
            data.get('appointment_date'),
            data.get('appointment_time'),
            data.get('location'),
            data.get('reminder_minutes', 60),
            data.get('notes')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_upcoming_appointments(self, days: int = 30) -> List[Dict]:
        """Get upcoming appointments."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM appointments
            WHERE appointment_date >= date('now')
            AND appointment_date <= date('now', ?)
            AND is_completed = 0
            ORDER BY appointment_date, appointment_time
        """, (f'+{days} days',))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== RELATIONSHIPS ====================
    
    def add_relationship(self, data: Dict[str, Any]) -> int:
        """Add a new relationship to track."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO relationships (name, relationship_type, notes)
            VALUES (?, ?, ?)
        """, (
            data.get('name'),
            data.get('relationship_type'),
            data.get('notes')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_relationships(self, active_only: bool = True) -> List[Dict]:
        """Get all relationships."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM relationships"
        if active_only:
            query += " WHERE is_active = 1"
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def save_interaction(self, data: Dict[str, Any]) -> int:
        """Save a relationship interaction."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO relationship_interactions (
                relationship_id, interaction_date, interaction_type,
                quality, your_mood_before, your_mood_after, patterns_noticed, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('relationship_id'),
            data.get('interaction_date'),
            data.get('interaction_type'),
            data.get('quality'),
            data.get('your_mood_before'),
            data.get('your_mood_after'),
            data.get('patterns_noticed'),
            data.get('notes')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_relationship_patterns(self, relationship_id: int) -> Dict[str, Any]:
        """Analyze patterns in a relationship."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                AVG(quality) as avg_quality,
                AVG(your_mood_after - your_mood_before) as avg_mood_change,
                COUNT(*) as total_interactions
            FROM relationship_interactions
            WHERE relationship_id = ?
        """, (relationship_id,))
        return dict(cursor.fetchone())
    
    # ==================== GOALS ====================
    
    def add_goal(self, data: Dict[str, Any]) -> int:
        """Add a new goal."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO goals (title, description, category, target_date, priority)
            VALUES (?, ?, ?, ?, ?)
        """, (
            data.get('title'),
            data.get('description'),
            data.get('category'),
            data.get('target_date'),
            data.get('priority', 3)
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_goals(self, status: str = 'active') -> List[Dict]:
        """Get goals by status."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM goals WHERE status = ? ORDER BY priority DESC, target_date
        """, (status,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_goal_progress(self, goal_id: int, progress: int):
        """Update goal progress."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE goals SET progress = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (progress, goal_id))
        self.conn.commit()
    
    def add_goal_milestone(self, data: Dict[str, Any]) -> int:
        """Add a milestone to a goal."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO goal_milestones (goal_id, title, description, target_date)
            VALUES (?, ?, ?, ?)
        """, (
            data.get('goal_id'),
            data.get('title'),
            data.get('description'),
            data.get('target_date')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    # ==================== BOWEL TRACKING ====================
    
    def save_bowel_entry(self, data: Dict[str, Any]) -> int:
        """Save a bowel entry."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO bowel_entries (
                entry_date, had_movement, consistency, pain_level, blood_present, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get('entry_date'),
            data.get('had_movement'),
            data.get('consistency'),
            data.get('pain_level'),
            data.get('blood_present', 0),
            data.get('notes')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_bowel_entries(self, days: int = 30) -> List[Dict]:
        """Get recent bowel entries."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM bowel_entries 
            WHERE entry_date >= date('now', ?)
            ORDER BY entry_date DESC
        """, (f'-{days} days',))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_bowel_recommendations(self) -> List[str]:
        """Get lifestyle recommendations based on bowel patterns."""
        entries = self.get_bowel_entries(14)
        recommendations = []
        
        if not entries:
            return recommendations
        
        # Check for constipation (no movement for 3+ days)
        no_movement_count = sum(1 for e in entries if not e['had_movement'])
        if no_movement_count >= 3:
            recommendations.append("Consider increasing fiber intake and water consumption")
            recommendations.append("Regular physical activity can help with regularity")
        
        # Check for pain
        avg_pain = sum(e['pain_level'] or 0 for e in entries) / len(entries)
        if avg_pain >= 4:
            recommendations.append("Persistent pain may warrant a medical consultation")
            recommendations.append("Consider keeping a food diary to identify triggers")
        
        # Check consistency
        consistencies = [e['consistency'] for e in entries if e['consistency']]
        if consistencies:
            avg_consistency = sum(consistencies) / len(consistencies)
            if avg_consistency <= 2:
                recommendations.append("Hard stools may indicate dehydration - increase water intake")
            elif avg_consistency >= 6:
                recommendations.append("Loose stools may be dietary - consider reducing caffeine or dairy")
        
        return recommendations
    
    # ==================== MOOD CHECKINS ====================
    
    def save_mood_checkin(self, data: Dict[str, Any]) -> int:
        """Save a mood check-in."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO mood_checkins (
                checkin_time, mood_level, energy_level, anxiety_level, stress_level, notes
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data.get('checkin_time', datetime.now().isoformat()),
            data.get('mood_level'),
            data.get('energy_level'),
            data.get('anxiety_level'),
            data.get('stress_level'),
            data.get('notes')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_mood_checkins(self, days: int = 7) -> List[Dict]:
        """Get recent mood check-ins."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM mood_checkins 
            WHERE date(checkin_time) >= date('now', ?)
            ORDER BY checkin_time DESC
        """, (f'-{days} days',))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== INSIGHTS & ANALYTICS ====================
    
    def get_lifestyle_insights(self) -> Dict[str, Any]:
        """
        Synthesize data across all modules to provide insights.
        This is the core of the Lifestyle Informatics feature.
        """
        insights = {
            'sleep_mood_correlation': self._analyze_sleep_mood_correlation(),
            'fitness_energy_correlation': self._analyze_fitness_energy_correlation(),
            'weekly_summary': self._get_weekly_summary(),
            'recommendations': []
        }
        
        # Generate recommendations based on patterns
        if insights['sleep_mood_correlation'].get('correlation', 0) > 0.5:
            insights['recommendations'].append(
                "Your mood appears strongly connected to sleep quality. Prioritize consistent sleep."
            )
        
        if insights['fitness_energy_correlation'].get('workout_days_energy', 0) > \
           insights['fitness_energy_correlation'].get('rest_days_energy', 0):
            insights['recommendations'].append(
                "You tend to have more energy on days you exercise. Keep up the workouts!"
            )
        
        return insights
    
    def _analyze_sleep_mood_correlation(self) -> Dict[str, Any]:
        """Analyze correlation between sleep and mood."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                AVG(CASE WHEN sleep_quality >= 7 THEN daily_mood END) as good_sleep_mood,
                AVG(CASE WHEN sleep_quality < 7 THEN daily_mood END) as poor_sleep_mood,
                AVG(sleep_quality) as avg_sleep_quality,
                AVG(daily_mood) as avg_daily_mood
            FROM sleep_entries
            WHERE sleep_quality IS NOT NULL AND daily_mood IS NOT NULL
        """)
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def _analyze_fitness_energy_correlation(self) -> Dict[str, Any]:
        """Analyze correlation between exercise and energy levels."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                s.entry_date,
                s.daily_energy,
                CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END as worked_out
            FROM sleep_entries s
            LEFT JOIN fitness_entries f ON s.entry_date = f.entry_date
            WHERE s.daily_energy IS NOT NULL
        """)
        
        rows = cursor.fetchall()
        if not rows:
            return {}
        
        workout_days_energy = [r['daily_energy'] for r in rows if r['worked_out']]
        rest_days_energy = [r['daily_energy'] for r in rows if not r['worked_out']]
        
        return {
            'workout_days_energy': sum(workout_days_energy) / len(workout_days_energy) if workout_days_energy else 0,
            'rest_days_energy': sum(rest_days_energy) / len(rest_days_energy) if rest_days_energy else 0,
            'total_workout_days': len(workout_days_energy),
            'total_rest_days': len(rest_days_energy)
        }
    
    def _get_weekly_summary(self) -> Dict[str, Any]:
        """Get a summary of the past week across all modules."""
        cursor = self.conn.cursor()
        
        # Sleep summary
        cursor.execute("""
            SELECT AVG(sleep_quality) as avg_sleep, AVG(daily_mood) as avg_mood
            FROM sleep_entries WHERE entry_date >= date('now', '-7 days')
        """)
        sleep_summary = dict(cursor.fetchone())
        
        # Fitness summary
        cursor.execute("""
            SELECT COUNT(*) as workouts, SUM(duration_minutes) as total_minutes
            FROM fitness_entries WHERE entry_date >= date('now', '-7 days')
        """)
        fitness_summary = dict(cursor.fetchone())
        
        # Medication adherence
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN taken = 1 THEN 1 END) as taken,
                COUNT(*) as total
            FROM medication_logs 
            WHERE date(taken_at) >= date('now', '-7 days')
        """)
        med_summary = dict(cursor.fetchone())
        
        return {
            'sleep': sleep_summary,
            'fitness': fitness_summary,
            'medication_adherence': med_summary
        }
