from database import run_query, load_table_df
from datetime import datetime

def get_next_id(table_name, prefix):
    df = load_table_df(table_name)
    if df.empty:
        return f"{prefix}-001"
    nums = []
    for i in df['id']:
        try:
            num = int(str(i).split('-')[-1])
            nums.append(num)
        except ValueError:
            continue
    next_num = max(nums) + 1 if nums else 1
    return f"{prefix}-{next_num:03d}"

# Darbai CRUD
def add_darbas(data):
    task_id = get_next_id('darbai', 'D')
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M')
    query = 'INSERT INTO darbai (id, created_at, title, description, location, source, priority, status, due_date, completed_date, hours_spent, materials, actions_taken, result, related_fault_id, needs_specialist, needs_manager_decision, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    run_query(query, (task_id, created_at, data['title'], data['description'], data['location'], data['source'], data['priority'], data['status'], data['due_date'], data.get('completed_date'), data.get('hours_spent', 0), data.get('materials', ''), data.get('actions_taken', ''), data.get('result', ''), data.get('related_fault_id', ''), 1 if data.get('needs_specialist') else 0, 1 if data.get('needs_manager_decision') else 0, data.get('notes', '')), fetch=False)
    return task_id

def update_darbas(task_id, data):
    query = 'UPDATE darbai SET title=?, description=?, location=?, source=?, priority=?, status=?, due_date=?, completed_date=?, hours_spent=?, materials=?, actions_taken=?, result=?, related_fault_id=?, needs_specialist=?, needs_manager_decision=?, notes=? WHERE id=?'
    run_query(query, (data['title'], data['description'], data['location'], data['source'], data['priority'], data['status'], data['due_date'], data.get('completed_date'), data.get('hours_spent', 0), data.get('materials', ''), data.get('actions_taken', ''), data.get('result', ''), data.get('related_fault_id', ''), 1 if data.get('needs_specialist') else 0, 1 if data.get('needs_manager_decision') else 0, data.get('notes', ''), task_id), fetch=False)

def delete_darbas(task_id):
    run_query("DELETE FROM darbai WHERE id=?", (task_id,), fetch=False)

# Gedimai CRUD
def add_gedimas(data):
    fault_id = get_next_id('gedimai', 'G')
    noticed_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    query = 'INSERT INTO gedimai (id, noticed_date, object_name, location, description, risk_level, is_safe_to_use, temporary_safety_measures, required_repair, assigned_specialist, sent_to_specialist_date, status, resolved_date, recheck_date, is_repeated, related_task_id, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    run_query(query, (fault_id, noticed_date, data['object_name'], data['location'], data['description'], data['risk_level'], 1 if data.get('is_safe_to_use', True) else 0, data.get('temporary_safety_measures', ''), data.get('required_repair', ''), data.get('assigned_specialist', ''), data.get('sent_to_specialist_date', ''), data['status'], data.get('resolved_date', ''), data.get('recheck_date', ''), 1 if data.get('is_repeated', False) else 0, data.get('related_task_id', ''), data.get('notes', '')), fetch=False)
    return fault_id

def update_gedimas(fault_id, data):
    query = 'UPDATE gedimai SET object_name=?, location=?, description=?, risk_level=?, is_safe_to_use=?, temporary_safety_measures=?, required_repair=?, assigned_specialist=?, sent_to_specialist_date=?, status=?, resolved_date=?, recheck_date=?, is_repeated=?, related_task_id=?, notes=? WHERE id=?'
    run_query(query, (data['object_name'], data['location'], data['description'], data['risk_level'], 1 if data.get('is_safe_to_use', True) else 0, data.get('temporary_safety_measures', ''), data.get('required_repair', ''), data.get('assigned_specialist', ''), data.get('sent_to_specialist_date', ''), data['status'], data.get('resolved_date', ''), data.get('recheck_date', ''), 1 if data.get('is_repeated', False) else 0, data.get('related_task_id', ''), data.get('notes', ''), fault_id), fetch=False)

def delete_gedimas(fault_id):
    run_query("DELETE FROM gedimai WHERE id=?", (fault_id,), fetch=False)

# Profilaktika CRUD
def add_profilaktika(data):
    p_id = get_next_id('profilaktika', 'P')
    query = 'INSERT INTO profilaktika (id, object_name, location, description, periodicity, last_check_date, next_check_date, status, result, flaws_found, related_fault_id, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    run_query(query, (p_id, data['object_name'], data.get('location', ''), data.get('description', ''), data['periodicity'], data.get('last_check_date', ''), data.get('next_check_date', ''), data['status'], data.get('result', ''), data.get('flaws_found', ''), data.get('related_fault_id', ''), data.get('notes', '')), fetch=False)
    return p_id

def update_profilaktika(p_id, data):
    query = 'UPDATE profilaktika SET object_name=?, location=?, description=?, periodicity=?, last_check_date=?, next_check_date=?, status=?, result=?, flaws_found=?, related_fault_id=?, notes=? WHERE id=?'
    run_query(query, (data['object_name'], data.get('location', ''), data.get('description', ''), data['periodicity'], data.get('last_check_date', ''), data.get('next_check_date', ''), data['status'], data.get('result', ''), data.get('flaws_found', ''), data.get('related_fault_id', ''), data.get('notes', ''), p_id), fetch=False)

def delete_profilaktika(p_id):
    run_query("DELETE FROM profilaktika WHERE id=?", (p_id,), fetch=False)

# Islaidos CRUD
def add_islaidos(data):
    e_id = get_next_id('islaidos', 'I')
    total = float(data.get('quantity', 1)) * float(data.get('unit_price', 0))
    query = 'INSERT INTO islaidos (id, date, item_name, category, quantity, unit_price, total_amount, related_task_id, supplier, invoice_number, is_approved, approved_by, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    run_query(query, (e_id, data['date'], data['item_name'], data['category'], data.get('quantity', 1), data.get('unit_price', 0), total, data.get('related_task_id', ''), data.get('supplier', ''), data.get('invoice_number', ''), 1 if data.get('is_approved', False) else 0, data.get('approved_by', ''), data.get('notes', '')), fetch=False)
    return e_id

def update_islaidos(e_id, data):
    total = float(data.get('quantity', 1)) * float(data.get('unit_price', 0))
    query = 'UPDATE islaidos SET date=?, item_name=?, category=?, quantity=?, unit_price=?, total_amount=?, related_task_id=?, supplier=?, invoice_number=?, is_approved=?, approved_by=?, notes=? WHERE id=?'
    run_query(query, (data['date'], data['item_name'], data['category'], data.get('quantity', 1), data.get('unit_price', 0), total, data.get('related_task_id', ''), data.get('supplier', ''), data.get('invoice_number', ''), 1 if data.get('is_approved', False) else 0, data.get('approved_by', ''), data.get('notes', ''), e_id), fetch=False)

def delete_islaidos(e_id):
    run_query("DELETE FROM islaidos WHERE id=?", (e_id,), fetch=False)
