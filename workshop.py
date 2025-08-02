import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import os
from email_validator import validate_email, EmailNotValidError
import requests
from io import BytesIO
import csv

# --------------------- CONFIGURATION ---------------------
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

CERT_TEMPLATE_URL = "https://raw.githubusercontent.com/krishnagollapelli/excelrate-cert-app/main/assets/certificate_template.jpg"

FONT_PATH = "arial.ttf"
FONT_SIZE = 60
TEXT_POSITION = (700, 800)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # You can move this to environment vars
# ----------------------------------------------------------

# -------------- Session State for Login -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_type = None
# ----------------------------------------------------------

# -------------- Session State for Feedback Submission -------
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
# ------------------------------------------------------------

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
# ----------------------------------------------------------

# ------------------ Admin Dashboard -----------------------
def admin_dashboard():
    st.title("🛡️ Admin Panel")
    st.markdown("View submitted feedback:")
    
    feedback_file = "feedback_data.csv"
    if os.path.exists(feedback_file):
        with open(feedback_file, "r") as f:
            rows = list(csv.reader(f))
            if rows:
                headers = rows[0]
                data = rows[1:]
                st.dataframe(data, use_container_width=True)
                st.download_button("📥 Download CSV", f.read(), "feedback_data.csv")
            else:
                st.info("No feedback yet.")
    else:
        st.info("No feedback submitted.")
# ----------------------------------------------------------

# ------------------ User Portal (Main) --------------------
def user_portal():
    st.title("📢 Excelrate User Portal")

    # Show feedback form first if not submitted yet
    if not st.session_state.feedback_submitted:
        st.header("📋 Submit Your Feedback First")

        name_fb = st.text_input("Full Name", key="name_fb")
        email_fb = st.text_input("Email", key="email_fb")
        feedback = st.text_area("Your Feedback", key="feedback")

        if st.button("Submit Feedback", key="submit_feedback"):
            if not name_fb or not email_fb or not feedback:
                st.warning("Please fill in all the fields.")
            else:
                try:
                    valid = validate_email(email_fb)
                    email_fb = valid.email

                    # Save to CSV
                    with open("feedback_data.csv", "a", newline="") as f:
                        writer = csv.writer(f)
                        if os.stat("feedback_data.csv").st_size == 0:
                            writer.writerow(["Name", "Email", "Feedback"])
                        writer.writerow([name_fb, email_fb, feedback])

                    st.success(f"Thanks for your feedback, {name_fb}!")
                    st.write("Your feedback:")
                    st.info(feedback)

                    # Mark feedback submitted for access to certificate
                    st.session_state.feedback_submitted = True

                except EmailNotValidError as e:
                    st.error(f"Invalid Email: {e}")

        st.info("You will be able to get your certificate after submitting feedback.")

    else:
        # Feedback submitted — show tabs for both feedback and certificate
        tab1, tab2 = st.tabs(["Feedback Submission", "Get Certificate"])

        with tab1:
            st.header("📋 Submit Your Feedback")
            name_fb = st.text_input("Full Name", key="name_fb_2")
            email_fb = st.text_input("Email", key="email_fb_2")
            feedback = st.text_area("Your Feedback", key="feedback_2")

            if st.button("Submit Feedback", key="submit_feedback_2"):
                if not name_fb or not email_fb or not feedback:
                    st.warning("Please fill in all the fields.")
                else:
                    try:
                        valid = validate_email(email_fb)
                        email_fb = valid.email

                        with open("feedback_data.csv", "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([name_fb, email_fb, feedback])

                        st.success(f"Thanks for your feedback, {name_fb}!")
                        st.write("Your feedback:")
                        st.info(feedback)
                    except EmailNotValidError as e:
                        st.error(f"Invalid Email: {e}")

        with tab2:
            st.header("🎓 Get Your Certificate")
            name_cert = st.text_input("Full Name", key="name_cert")
            email_cert = st.text_input("Email", key="email_cert")

            if st.button("Generate & Email Certificate", key="send_cert"):
                if not name_cert or not email_cert:
                    st.warning("Please enter your name and email.")
                else:
                    try:
                        valid = validate_email(email_cert)
                        email_cert = valid.email

                        # Load certificate template
                        response = requests.get(CERT_TEMPLATE_URL)
                        cert_img = Image.open(BytesIO(response.content)).convert("RGB")

                        # Draw name
                        draw = ImageDraw.Draw(cert_img)
                        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
                        draw.text(TEXT_POSITION, name_cert, font=font, fill="black")

                        cert_filename = f"{name_cert.replace(' ', '_')}_certificate.jpg"
                        cert_img.save(cert_filename)

                        pdf_filename = cert_filename.replace(".jpg", ".pdf")
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.image(cert_filename, x=0, y=0, w=210, h=297)
                        pdf.output(pdf_filename)

                        # Email
                        msg = EmailMessage()
                        msg['Subject'] = 'Your Certificate from Excelrate!'
                        msg['From'] = EMAIL_SENDER
                        msg['To'] = email_cert
                        msg.set_content(
                            f"Dear {name_cert},\n\nThank you for participating!\nPlease find your certificate attached.\n\nRegards,\nExcelrate Team"
                        )
                        with open(pdf_filename, 'rb') as f:
                            msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=pdf_filename)

                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                            smtp.send_message(msg)

                        st.success("✅ Certificate sent to your email!")
                        os.remove(cert_filename)
                        os.remove(pdf_filename)

                    except EmailNotValidError as e:
                        st.error(f"Invalid Email: {e}")
                    except Exception as e:
                        st.error(f"Something went wrong: {e}")
# ----------------------------------------------------------

# ------------------------ MAIN ----------------------------
if not st.session_state.logged_in:
    login()
elif st.session_state.user_type == "admin":
    admin_dashboard()
else:
    user_portal()
