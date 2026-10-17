import streamlit as st

def set_page_config():
    st.set_page_config(page_title="Ūkvedžio knygelė", page_icon="🛠️", layout="wide", initial_sidebar_state="expanded")

def apply_custom_css():
    st.markdown('''
        <style>
        .main { background-color: #F9F9F9; }
        .stButton>button { width: 100%; border-radius: 6px; font-weight: 600; }
        </style>
    ''', unsafe_allow_html=True)
