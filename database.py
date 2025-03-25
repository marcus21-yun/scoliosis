import sqlite3
from datetime import datetime
import threading

class Database:
    def __init__(self):
        self.db_path = 'scoliosis.db'
        self._create_tables()
        self._local = threading.local()
    
    def _get_connection(self):
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_path)
        return self._local.connection
    
    def _create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 사용자 정보 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                height REAL,
                weight REAL,
                scoliosis_type TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # 진단 기록 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                test_type TEXT NOT NULL,
                result REAL NOT NULL,
                image_path TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # 운동 기록 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise_name TEXT NOT NULL,
                completed BOOLEAN NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, name, age, gender, height=None, weight=None, scoliosis_type=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, age, gender, height, weight, scoliosis_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, age, gender, height, weight, scoliosis_type, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        return cursor.lastrowid
    
    def get_user(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()
    
    def update_user(self, user_id, height=None, weight=None, scoliosis_type=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        updates = []
        values = []
        if height is not None:
            updates.append('height = ?')
            values.append(height)
        if weight is not None:
            updates.append('weight = ?')
            values.append(weight)
        if scoliosis_type is not None:
            updates.append('scoliosis_type = ?')
            values.append(scoliosis_type)
        
        if updates:
            values.append(user_id)
            cursor.execute(f'''
                UPDATE users 
                SET {', '.join(updates)}
                WHERE id = ?
            ''', values)
            conn.commit()
    
    def add_diagnosis(self, user_id, test_type, result, image_path=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO diagnoses (user_id, test_type, result, image_path, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, test_type, result, image_path, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
    
    def get_all_diagnoses(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.*, u.name, u.scoliosis_type 
            FROM diagnoses d 
            JOIN users u ON d.user_id = u.id 
            ORDER BY d.created_at DESC
        ''')
        return cursor.fetchall()
    
    def get_user_diagnoses(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM diagnoses 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (user_id,))
        return cursor.fetchall()
    
    def add_exercise(self, user_id, exercise_name, completed, date):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO exercises (user_id, exercise_name, completed, date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, exercise_name, completed, date))
        conn.commit()
    
    def get_all_exercises(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.*, u.name 
            FROM exercises e 
            JOIN users u ON e.user_id = u.id 
            ORDER BY e.date DESC
        ''')
        return cursor.fetchall()
    
    def get_user_exercises(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM exercises 
            WHERE user_id = ? 
            ORDER BY date DESC
        ''', (user_id,))
        return cursor.fetchall() 