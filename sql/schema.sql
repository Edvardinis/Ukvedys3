-- Ūkvedžio knygelė Database Schema

CREATE TABLE IF NOT EXISTS darbai (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    location TEXT,
    source TEXT,
    priority TEXT,
    status TEXT,
    due_date TEXT,
    completed_date TEXT,
    hours_spent REAL DEFAULT 0,
    materials TEXT,
    actions_taken TEXT,
    result TEXT,
    related_fault_id TEXT,
    needs_specialist BOOLEAN DEFAULT 0,
    needs_manager_decision BOOLEAN DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS gedimai (
    id TEXT PRIMARY KEY,
    noticed_date TEXT NOT NULL,
    object_name TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT,
    risk_level TEXT,
    is_safe_to_use BOOLEAN DEFAULT 1,
    temporary_safety_measures TEXT,
    required_repair TEXT,
    assigned_specialist TEXT,
    sent_to_specialist_date TEXT,
    status TEXT,
    resolved_date TEXT,
    recheck_date TEXT,
    is_repeated BOOLEAN DEFAULT 0,
    related_task_id TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS profilaktika (
    id TEXT PRIMARY KEY,
    object_name TEXT NOT NULL,
    location TEXT,
    description TEXT,
    periodicity TEXT,
    last_check_date TEXT,
    next_check_date TEXT,
    status TEXT,
    result TEXT,
    flaws_found TEXT,
    related_fault_id TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS islaidos (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity REAL DEFAULT 1,
    unit_price REAL DEFAULT 0,
    total_amount REAL DEFAULT 0,
    related_task_id TEXT,
    supplier TEXT,
    invoice_number TEXT,
    is_approved BOOLEAN DEFAULT 0,
    approved_by TEXT,
    notes TEXT
);
