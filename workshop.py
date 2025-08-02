import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import os
from email_validator import validate_email, EmailNotValidError
import requests
from io import BytesIO
import sqlite3
import pandas as pd

# --------------------- CONFIGURATION ---------------------
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

CERT_TEMPLATE_URL = "https://raw.githubusercontent.com/krishnagollapelli/excelrate-cert-app/main/assets/certificate_template.jpg"

FONT_PATH = "arial.ttf"
FONT_SIZE = 60
TEXT_POSITION = (700, 800)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # Better to use env variables

DB_PATH = "feedback.db"
# ----------------------------------------------------------

# -------------------- Database Setup -----------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            feedback TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_feedback(name, email, feedback_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO feedback (name, email, feedback) VALUES (?, ?, ?)
    ''', (name, email, feedback_text))
    conn.commit()
    conn.close()

def get_all_feedback():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM feedback ORDER BY timestamp DESC", conn)
    conn.close()
    return df
# ----------------------------------------------------------

# ---------------------- Login UI --------------------------
def login():
    st.title("🔐 Login to Excelrate Portal")
    user = st.text_input("Username")
    passwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == ADMIN_USERNAME and passwd == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.user_type = "admin"
        else:
            st.session_state.logged_in = True
            st.session_state.user_type = "user"
        st.experimental_rerun()
# ----------------------------------------------------------

# ------------------ Logout Button -------------------------
def logout_button():
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.feedback_submitted = False
        st.exper
