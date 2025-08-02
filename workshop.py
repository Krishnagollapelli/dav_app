import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

# Inject CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("styles.css")

st.title("🎓 Excelrate Workshop Feedback & Certificate")

# Form
with st.form("feedback_form"):
    st.subheader("📋 Feedback Form")
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    rating = st.slider("Workshop Rating", 1, 5)
    comments = st.text_area("Comments or Suggestions")
    submit = st.form_submit_button("Submit and Receive Certificate")

# Certificate Generator
def generate_certificate(name, cert_path):
    try:
        if os.path.exists("certificate_template.png"):
            template = Image.open("certificate_template.png")
        else:
            template = Image.new("RGB", (1200, 800), color=(255, 255, 255))

        draw = ImageDraw.Draw(template)
        font = ImageFont.truetype("arial.ttf", 60)
        draw.text((300, 350), "Certificate of Participation", font=font, fill="black")
        draw.text((300, 450), f"Awarded to: {name}", font=font, fill="black")
        template.save(cert_path)
    except Exception as e:
        st.error(f"Certificate generation failed: {e}")

# Email Sender
def send_certificate(email_to, name, cert_path):
    msg = EmailMessage()
    msg['Subject'] = "🎉 Your Workshop Certificate - Excelrate"
    msg['From'] = os.getenv("EMAIL_ID")
    msg['To'] = email_to
    msg.set_content(
        f"Dear {name},\n\nThanks for attending Excelrate Workshop!\nPlease find your certificate attached.\n\nRegards,\nTeam Excelrate"
    )

    with open(cert_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(cert_path)
        msg.add_attachment(file_data, maintype='image', subtype='png', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.getenv("EMAIL_ID"), os.getenv("EMAIL_PASS"))
        smtp.send_message(msg)

# Handle Form Submission
if submit:
    if not name or not email:
        st.error("Please enter both name and email.")
    else:
        feedback = pd.DataFrame([[name, email, rating, comments]],
                                columns=["Name", "Email", "Rating", "Comments"])

        if os.path.exists("feedback.csv"):
            existing = pd.read_csv("feedback.csv")
            feedback = pd.concat([existing, feedback], ignore_index=True)
        feedback.to_csv("feedback.csv", index=False)

        cert_dir = "certificates"
        os.makedirs(cert_dir, exist_ok=True)
        cert_path = os.path.join(cert_dir, f"{name.replace(' ', '_')}.png")

        generate_certificate(name, cert_path)

        try:
            send_certificate(email, name, cert_path)
            st.success("✅ Feedback submitted and certificate sent!")
        except Exception as e:
            st.error(f"❌ Email failed: {e}")
