import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px

from utils import set_page_config, apply_custom_css
from database import init_db, load_table_df
from models import (
    add_darbas, update_darbas, delete_darbas,
    add_gedimas, update_gedimas, delete_gedimas,
    add_profilaktika, update_profilaktika, delete_profilaktika,
    add_islaidos, update_islaidos, delete_islaidos
)
from reports import generate_excel, generate_pdf_report

set_page_config()
apply_custom_css()
init_db()

# Slaptažodžio apsauga (jei nustatyta secrets.toml)
if "auth" in st.secrets and "password" in st.secrets["auth"]:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 Prisijungimas prie Ūkvedžio knygelės")
        pwd = st.text_input("Įveskite slaptažodį", type="password")
        if st.button("Prisijungti"):
            if pwd == st.secrets["auth"]["password"]:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Neteisingas slaptažodis!")
        st.stop()

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

tasks_df = load_table_df("darbai")
faults_df = load_table_df("gedimai")
maintenance_df = load_table_df("profilaktika")
expenses_df = load_table_df("islaidos")

if menu == "🏠 Prietaisų skydelis":
    st.title("🏠 Prietaisų skydelis")
    today_str = date.today().strftime("%Y-%m-%d")
    
    today_tasks = len(tasks_df[tasks_df['due_date'] == today_str]) if not tasks_df.empty and 'due_date' in tasks_df.columns else 0
    open_tasks = len(tasks_df[tasks_df['status'] != 'Atlikta']) if not tasks_df.empty and 'status' in tasks_df.columns else 0
    overdue_tasks = len(tasks_df[(tasks_df['due_date'] < today_str) & (tasks_df['status'] != 'Atlikta')]) if not tasks_df.empty and 'due_date' in tasks_df.columns else 0
    urgent_faults = len(faults_df[(faults_df['risk_level'] == 'Kritinė') & (faults_df['status'] != 'Pašalintas')]) if not faults_df.empty and 'risk_level' in faults_df.columns else 0
    monthly_expenses = expenses_df['total_amount'].sum() if not expenses_df.empty and 'total_amount' in expenses_df.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Šiandienos darbai", today_tasks)
        st.metric("Neatliktos užduotys", open_tasks)
    with col2:
        st.metric("Vėluojantys darbai", overdue_tasks)
        st.metric("Kritinės problemos", urgent_faults)
    with col3:
        completed_count = len(tasks_df[tasks_df['status'] == 'Atlikta']) if not tasks_df.empty else 0
        st.metric("Atlikti darbai", completed_count)
        st.metric("Atviri gedimai", len(faults_df[faults_df['status'] != 'Pašalintas']) if not faults_df.empty else 0)
    with col4:
        st.metric("Bendros išlaidos", f"{monthly_expenses:.2f} €")

elif menu == "📋 Darbų žurnalas":
    st.title("📋 Darbų žurnalas")
    tab1, tab2 = st.tabs(["Darbų sąrašas", "Pridėti naują darbą"])
    with tab1:
        if tasks_df.empty:
            st.info("Nėra darbų.")
        else:
            st.dataframe(tasks_df, use_container_width=True)
            sel_id = st.selectbox("Pasirinkite ID trynimui", tasks_df['id'].tolist())
            if st.button("Ištrinti darbą"):
                delete_darbas(sel_id)
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
                    add_darbas({'title': title, 'description': desc, 'location': loc, 'source': 'Vadovo pavedimas', 'priority': priority, 'status': 'Nauja', 'due_date': str(due)})
                    st.success("Sukurta!")
                    st.rerun()

elif menu == "⚠️ Gedimų registras":
    st.title("⚠️ Gedimų registras")
    tab1, tab2 = st.tabs(["Sąrašas", "Registruoti"])
    with tab1:
        if faults_df.empty:
            st.info("Nėra gedimų.")
        else:
            st.dataframe(faults_df, use_container_width=True)
    with tab2:
        with st.form("new_fault"):
            obj = st.text_input("Objektas *")
            loc = st.text_input("Vieta *")
            desc = st.text_area("Aprašymas")
            risk = st.selectbox("Rizika", ["Maža", "Vidutinė", "Aukšta", "Kritinė"])
            if st.form_submit_button("Registruoti"):
                if obj:
                    add_gedimas({'object_name': obj, 'location': loc, 'description': desc, 'risk_level': risk, 'status': 'Naujas'})
                    st.success("Užregistruota!")
                    st.rerun()

elif menu == "🔄 Profilaktinė priežiūra":
    st.title("🔄 Profilaktinė priežiūra")
    if maintenance_df.empty:
        st.info("Nėra patikrų.")
    else:
        st.dataframe(maintenance_df, use_container_width=True)
    with st.form("new_maint"):
        obj = st.text_input("Objektas *")
        period = st.selectbox("Periodiškumas", ["kas mėnesį", "kas ketvirtį", "kasmet"])
        if st.form_submit_button("Pridėti"):
            if obj:
                add_profilaktika({'object_name': obj, 'periodicity': period, 'status': 'Planuojama'})
                st.success("Pridėta!")
                st.rerun()

elif menu == "💶 Medžiagos ir išlaidos":
    st.title("💶 Medžiagos ir išlaidos")
    if expenses_df.empty:
        st.info("Nėra išlaidų.")
    else:
        st.dataframe(expenses_df, use_container_width=True)
    with st.form("new_exp"):
        item = st.text_input("Prekė *")
        cat = st.selectbox("Kategorija", ["įrankiai", "santechnika", "elektros prekės", "kita"])
        qty = st.number_input("Kiekis", value=1.0)
        price = st.number_input("Vieneto kaina (€)", value=0.0)
        if st.form_submit_button("Registruoti išlaidą"):
            if item:
                add_islaidos({'date': str(date.today()), 'item_name': item, 'category': cat, 'quantity': qty, 'unit_price': price})
                st.success("Užregistruota!")
                st.rerun()

elif menu == "📊 Statistika ir analizė":
    st.title("📊 Statistika ir analizė")
    if not tasks_df.empty:
        fig = px.pie(tasks_df, names='priority', title="Darbų pasiskirstymas pagal prioritetą")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Trūksta duomenų statistikai.")

elif menu == "📑 Ataskaitos":
    st.title("📑 Ataskaitos vadovui")
    summary_data = {
        'date': str(date.today()),
        'total_tasks': len(tasks_df),
        'completed_tasks': len(tasks_df[tasks_df['status'] == 'Atlikta']) if not tasks_df.empty else 0,
        'open_tasks': len(tasks_df[tasks_df['status'] != 'Atlikta']) if not tasks_df.empty else 0,
        'total_expenses': expenses_df['total_amount'].sum() if not expenses_df.empty else 0,
        'notes_text': 'Visi darbai vykdomi pagal planą.'
    }
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Atsisiųsti PDF"):
            pdf = generate_pdf_report(summary_data)
            st.download_button("Parsisiųsti PDF", pdf, file_name="ataskaita.pdf", mime="application/pdf")
    with col2:
        if st.button("📊 Atsisiųsti Excel"):
            exc = generate_excel(tasks_df, faults_df, maintenance_df, expenses_df)
            st.download_button("Parsisiųsti Excel", exc, file_name="duomenys.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
