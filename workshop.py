import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import os
from email_validator import validate_email, EmailNotValidError
import requests
from io import BytesIO

# --------------------- CONFIGURATION ---------------------
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

CERT_TEMPLATE_URL = "https://raw.githubusercontent.com/krishnagollapelli/excelrate-cert-app/main/assets/certificate_template.jpg"

FONT_PATH = "arial.ttf"
FONT_SIZE = 60
TEXT_POSITION = (700, 800)
# ----------------------------------------------------------

st.title("🔁 Excelrate Workshop")

tab1, tab2 = st.tabs(["Feedback Submission", "Get Certificate"])

# ------ TAB 1: Feedback Submission ------
with tab1:
    st.header("📋 Submit Your Feedback")
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
                # Here you can save feedback to a database or CSV if you want
                st.success(f"Thanks for your feedback, {name_fb}!")
                st.write("Your feedback:")
                st.info(feedback)
            except EmailNotValidError as e:
                st.error(f"Invalid Email: {e}")

# ------ TAB 2: Get Certificate ------
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

                # Load certificate template from GitHub URL
                response = requests.get(CERT_TEMPLATE_URL)
                cert_img = Image.open(BytesIO(response.content)).convert("RGB")

                # Draw name on certificate
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
