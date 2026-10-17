import streamlit as st
import pandas as pd
from datetime import datetime, date
import sqlite3
import plotly.express as px

# --- Puslapio konfigūracija ---
st.set_page_config(
    page_title="Ūkvedžio knygelė",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #F9F9F9; }
    .stButton>button { width: 100%; border-radius: 6px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- Duomenų bazės inicializavimas ---
DB_NAME = "ukvedys.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS darbai (
        id TEXT PRIMARY KEY, created_at TEXT, title TEXT, description TEXT, 
        location TEXT, source TEXT, priority TEXT, status TEXT, due_date TEXT, 
        completed_date TEXT, hours_spent REAL, materials TEXT, notes TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS gedimai (
        id TEXT PRIMARY KEY, noticed_date TEXT, object_name TEXT, location TEXT, 
        description TEXT, risk_level TEXT, status TEXT, notes TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS profilaktika (
        id TEXT PRIMARY KEY, object_name TEXT, periodicity TEXT, status TEXT, notes TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS islaidos (
        id TEXT PRIMARY KEY, date TEXT, item_name TEXT, category TEXT, 
        quantity REAL, unit_price REAL, total_amount REAL, notes TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def load_df(table):
    conn = get_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
    except Exception:
        df = pd.DataFrame()
    finally:
        conn.close()
    return df

def get_next_id(table, prefix):
    df = load_df(table)
    if df.empty:
        return f"{prefix}-001"
    nums = []
    for i in df['id']:
        try:
            nums.append(int(str(i).split('-')[-1]))
        except:
            continue
    return f"{prefix}-{max(nums) + 1:03d}" if nums else f"{prefix}-001"

# --- Navigacija ---
st.sidebar.title("🛠️ Ūkvedžio knygelė")
menu = st.sidebar.radio(
    "Navigacija",
    [
        "🏠 Prietaisų skydelis",
        "📋 Darbų žurnalas",
        "⚠️ Gedimų registras",
        "🔄 Profilaktinė priežiūra",
        "💶 Medžiagos ir išlaidos",
        "📊 Statistika ir analizė",
        "📑 Ataskaitos"
    ]
)

tasks_df = load_df("darbai")
faults_df = load_df("gedimai")
maintenance_df = load_df("profilaktika")
expenses_df = load_df("islaidos")

# --- 1. SKYDELIS ---
if menu == "🏠 Prietaisų skydelis":
    st.title("🏠 Prietaisų skydelis")
    today_str = date.today().strftime("%Y-%m-%d")
    
    today_tasks = len(tasks_df[tasks_df['due_date'] == today_str]) if not tasks_df.empty and 'due_date' in tasks_df.columns else 0
    open_tasks = len(tasks_df[tasks_df['status'] != 'Atlikta']) if not tasks_df.empty and 'status' in tasks_df.columns else 0
    open_faults = len(faults_df[faults_df['status'] != 'Pašalintas']) if not faults_df.empty and 'status' in faults_df.columns else 0
    monthly_exp = expenses_df['total_amount'].sum() if not expenses_df.empty and 'total_amount' in expenses_df.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Šiandienos darbai", today_tasks)
    with c2: st.metric("Neatliktos užduotys", open_tasks)
    with c3: st.metric("Atviri gedimai", open_faults)
    with c4: st.metric("Išlaidos iš viso", f"{monthly_exp:.2f} €")

# --- 2. DARBAI ---
elif menu == "📋 Darbų žurnalas":
    st.title("📋 Darbų žurnalas")
    tab1, tab2 = st.tabs(["Sąrašas", "Pridėti naują"])
    with tab1:
        if tasks_df.empty:
            st.info("Nėra darbų.")
        else:
            st.dataframe(tasks_df, use_container_width=True)
            del_id = st.selectbox("Pasirinkite ID šalinimui", tasks_df['id'].tolist() if not tasks_df.empty else [])
            if st.button("Ištrinti darbą") and del_id:
                conn = get_connection()
                conn.execute("DELETE FROM darbai WHERE id=?", (del_id,))
                conn.commit()
                conn.close()
                st.success("Ištrinta!")
                st.rerun()
    with tab2:
        with st.form("new_task"):
            title = st.text_input("Pavadinimas *")
            desc = st.text_area("Aprašymas")
            loc = st.text_input("Vieta")
            priority = st.selectbox("Prioritetas", ["P1 - Kritinė", "P2 - Skubi", "P3 - Įprasta", "P4 - Planinė"])
            due = st.date_input("Terminas", date.today())
            if st.form_submit_button("Sukurti"):
                if title:
                    tid = get_next_id("darbai", "D")
                    conn = get_connection()
                    conn.execute("INSERT INTO darbai VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 (tid, datetime.now().strftime('%Y-%m-%d %H:%M'), title, desc, loc, 'Vadovo pavedimas', priority, 'Nauja', str(due), '', 0.0, '', ''))
                    conn.commit()
                    conn.close()
                    st.success("Sukurta sėkmingai!")
                    st.rerun()

# --- 3. GEDIMAI ---
elif menu == "⚠️ Gedimų registras":
    st.title("⚠️ Gedimų registras")
    tab1, tab2 = st.tabs(["Sąrašas", "Registruoti"])
    with tab1:
        if faults_df.empty:
            st.info("Nėra gedimų.")
        else:
            st.dataframe(faults_df, use_container_width=True)
            # Pridėta galimybė ištrinti gedimą pagal ID
            del_fault_id = st.selectbox("Pasirinkite gedimo ID šalinimui", faults_df['id'].tolist() if not faults_df.empty else [])
            if st.button("Ištrinti gedimą") and del_fault_id:
                conn = get_connection()
                conn.execute("DELETE FROM gedimai WHERE id=?", (del_fault_id,))
                conn.commit()
                conn.close()
                st.success("Gedimas sėkmingai ištrintas!")
                st.rerun()
    with tab2:
        with st.form("new_fault"):
            obj = st.text_input("Objektas *")
            loc = st.text_input("Vieta *")
            desc = st.text_area("Aprašymas")
            risk = st.selectbox("Rizika", ["Maža", "Vidutinė", "Aukšta", "Kritinė"])
            if st.form_submit_button("Registruoti"):
                if obj:
                    fid = get_next_id("gedimai", "G")
                    conn = get_connection()
                    conn.execute("INSERT INTO gedimai VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                 (fid, datetime.now().strftime('%Y-%m-%d %H:%M'), obj, loc, desc, risk, 'Naujas', ''))
                    conn.commit()
                    conn.close()
                    st.success("Užregistruota!")
                    st.rerun()

# --- 4. PROFILAKTIKA ---
elif menu == "🔄 Profilaktinė priežiūra":
    st.title("🔄 Profilaktinė priežiūra")
    if not maintenance_df.empty:
        st.dataframe(maintenance_df, use_container_width=True)
    else:
        st.info("Nėra patikrų.")
    with st.form("new_maint"):
        obj = st.text_input("Objektas *")
        period = st.selectbox("Periodiškumas", ["kas mėnesį", "kas ketvirtį", "kasmet"])
        if st.form_submit_button("Pridėti"):
            if obj:
                pid = get_next_id("profilaktika", "P")
                conn = get_connection()
                conn.execute("INSERT INTO profilaktika VALUES (?, ?, ?, ?, ?)", (pid, obj, period, 'Planuojama', ''))
                conn.commit()
                conn.close()
                st.success("Pridėta!")
                st.rerun()

# --- 5. IŠLAIDOS ---
elif menu == "💶 Medžiagos ir išlaidos":
    st.title("💶 Medžiagos ir išlaidos")
    if not expenses_df.empty:
        st.dataframe(expenses_df, use_container_width=True)
    else:
        st.info("Nėra išlaidų.")
    with st.form("new_exp"):
        item = st.text_input("Prekė *")
        cat = st.selectbox("Kategorija", ["įrankiai", "santechnika", "elektros prekės", "kita"])
        qty = st.number_input("Kiekis", value=1.0)
        price = st.number_input("Vieneto kaina (€)", value=0.0)
        if st.form_submit_button("Registruoti"):
            if item:
                eid = get_next_id("islaidos", "I")
                tot = qty * price
                conn = get_connection()
                conn.execute("INSERT INTO islaidos VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (eid, str(date.today()), item, cat, qty, price, tot, ''))
                conn.commit()
                conn.close()
                st.success("Užregistruota!")
                st.rerun()

# --- 6. STATISTIKA ---
elif menu == "📊 Statistika ir analizė":
    st.title("📊 Statistika ir analizė")
    if not tasks_df.empty and 'priority' in tasks_df.columns:
        fig = px.pie(tasks_df, names='priority', title="Darbų pasiskirstymas pagal prioritetą")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trūksta duomenų statistikai.")

# --- 7. ATASKAITOS ---
elif menu == "📑 Ataskaitos":
    st.title("📑 Ataskaitos vadovui")
    total_t = len(tasks_df)
    comp_t = len(tasks_df[tasks_df['status'] == 'Atlikta']) if not tasks_df.empty else 0
    tot_exp = expenses_df['total_amount'].sum() if not expenses_df.empty else 0
    
    st.info(f"Ataskaitos duomenys: Iš viso darbų: {total_t}, Atlikta: {comp_t}, Išlaidos: {tot_exp:.2f} €")
    
    email_txt = f"Labas dieną,\n\nTeikiu ūkvedžio ataskaitą:\n- Iš viso darbų: {total_t}\n- Atlikta: {comp_t}\n- Išlaidos: {tot_exp:.2f} €\n\nPagarbiai,\nŪkvedys"
    st.text_area("Nukopijuokite tekstą el. laiškui:", email_txt, height=150)
