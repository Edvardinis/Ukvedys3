import sqlite3
import os
import pandas as pd

DB_NAME = "ukvedys.db"

def get_connection():
    try:
        import streamlit as st
        if "supabase" in st.secrets:
            import psycopg2
            cfg = st.secrets["supabase"]
            conn = psycopg2.connect(
                host=cfg["host"],
                database=cfg["database"],
                user=cfg["user"],
                password=cfg["password"],
                port=cfg.get("port", 5432)
            )
            return conn
    except Exception:
        pass
    
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    is_postgres = not isinstance(conn, sqlite3.Connection)
    
    if is_postgres:
        cursor.execute('CREATE TABLE IF NOT EXISTS darbai (id VARCHAR(50) PRIMARY KEY, created_at VARCHAR(50) NOT NULL, title TEXT NOT NULL, description TEXT, location TEXT, source TEXT, priority TEXT, status TEXT, due_date VARCHAR(50), completed_date VARCHAR(50), hours_spent REAL DEFAULT 0, materials TEXT, actions_taken TEXT, result TEXT, related_fault_id VARCHAR(50), needs_specialist BOOLEAN DEFAULT FALSE, needs_manager_decision BOOLEAN DEFAULT FALSE, notes TEXT);')
        cursor.execute('CREATE TABLE IF NOT EXISTS gedimai (id VARCHAR(50) PRIMARY KEY, noticed_date VARCHAR(50) NOT NULL, object_name TEXT NOT NULL, location TEXT NOT NULL, description TEXT, risk_level TEXT, is_safe_to_use BOOLEAN DEFAULT TRUE, temporary_safety_measures TEXT, required_repair TEXT, assigned_specialist TEXT, sent_to_specialist_date VARCHAR(50), status TEXT, resolved_date VARCHAR(50), recheck_date VARCHAR(50), is_repeated BOOLEAN DEFAULT FALSE, related_task_id VARCHAR(50), notes TEXT);')
        cursor.execute('CREATE TABLE IF NOT EXISTS profilaktika (id VARCHAR(50) PRIMARY KEY, object_name TEXT NOT NULL, location TEXT, description TEXT, periodicity TEXT, last_check_date VARCHAR(50), next_check_date VARCHAR(50), status TEXT, result TEXT, flaws_found TEXT, related_fault_id VARCHAR(50), notes TEXT);')
        cursor.execute('CREATE TABLE IF NOT EXISTS islaidos (id VARCHAR(50) PRIMARY KEY, date VARCHAR(50) NOT NULL, item_name TEXT NOT NULL, category TEXT NOT NULL, quantity REAL DEFAULT 1, unit_price REAL DEFAULT 0, total_amount REAL DEFAULT 0, related_task_id VARCHAR(50), supplier TEXT, invoice_number TEXT, is_approved BOOLEAN DEFAULT FALSE, approved_by TEXT, notes TEXT);')
    else:
        cursor.execute('CREATE TABLE IF NOT EXISTS darbai (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, title TEXT NOT NULL, description TEXT, location TEXT, source TEXT, priority TEXT, status TEXT, due_date TEXT, completed_date TEXT, hours_spent REAL DEFAULT 0, materials TEXT, actions_taken TEXT, result TEXT, related_fault_id TEXT, needs_specialist INTEGER DEFAULT 0, needs_manager_decision INTEGER DEFAULT 0, notes TEXT);')
        cursor.execute('CREATE TABLE IF NOT EXISTS gedimai (id TEXT PRIMARY KEY, noticed_date TEXT NOT NULL, object_name TEXT NOT NULL, location TEXT NOT NULL, description TEXT, risk_level TEXT, is_safe_to_use INTEGER DEFAULT 1, temporary_safety_measures TEXT, required_repair TEXT, assigned_specialist TEXT, sent_to_specialist_date TEXT, status TEXT, resolved_date TEXT, recheck_date TEXT, is_repeated INTEGER DEFAULT 0, related_task_id TEXT, notes TEXT);')
        cursor.execute('CREATE TABLE IF NOT EXISTS profilaktika (id TEXT PRIMARY KEY, object_name TEXT NOT NULL, location TEXT, description TEXT, periodicity TEXT, last_check_date TEXT, next_check_date TEXT, status TEXT, result TEXT, flaws_found TEXT, related_fault_id TEXT, notes TEXT);')
        cursor.execute('CREATE TABLE IF NOT EXISTS islaidos (id TEXT PRIMARY KEY, date TEXT NOT NULL, item_name TEXT NOT NULL, category TEXT NOT NULL, quantity REAL DEFAULT 1, unit_price REAL DEFAULT 0, total_amount REAL DEFAULT 0, related_task_id TEXT, supplier TEXT, invoice_number TEXT, is_approved INTEGER DEFAULT 0, approved_by TEXT, notes TEXT);')
    
    conn.commit()
    conn.close()

def run_query(query, params=(), fetch=True):
    conn = get_connection()
    is_postgres = not isinstance(conn, sqlite3.Connection)
    cursor = conn.cursor()
    if is_postgres:
        query = query.replace('?', '%s')
    cursor.execute(query, params)
    result = None
    if fetch:
        if is_postgres:
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in rows]
        else:
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
    conn.commit()
    conn.close()
    return result

def load_table_df(table_name):
    conn = get_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df
