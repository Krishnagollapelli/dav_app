import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# Streamlit UI
st.title("🎓 Workshop Feedback & Certificate")

with st.form("feedback_form"):
    st.subheader("📋 Feedback Form")
    name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    rating = st.slider("Workshop Rating (1 = Worst, 5 = Best)", 1, 5)
    comments = st.text_area("Comments / Suggestions")
    submit = st.form_submit_button("Submit and Receive Certificate")

# Function to generate certificate
def generate_certificate(name, cert_path):
    template = Image.open("certificate_template.png")  # Use your own certificate template image
    draw = ImageDraw.Draw(template)
    font = ImageFont.truetype("arial.ttf", 60)  # Use a suitable font path
    text_position = (500, 450)  # Adjust this based on your template
    draw.text(text_position, name, fill="black", font=font)
    template.save(cert_path)

# Function to send email with certificate
def send_certificate(email_to, name, cert_path):
    msg = EmailMessage()
    msg['Subject'] = "🎉 Your Workshop Certificate - Excelrate"
    msg['From'] = os.getenv("EMAIL_ID")
    msg['To'] = email_to
    msg.set_content(f"Dear {name},\n\nThanks for attending our workshop and submitting your feedback!\nPlease find your certificate attached.\n\nRegards,\nTeam Excelrate")

    with open(cert_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(cert_path)
        msg.add_attachment(file_data, maintype='image', subtype='png', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.getenv("EMAIL_ID"), os.getenv("EMAIL_PASS"))
        smtp.send_message(msg)

# Process form submission
if submit:
    if not name or not email:
        st.error("Please fill in both Name and Email.")
    else:
        # Save feedback
        feedback = pd.DataFrame([[name, email, rating, comments]],
                                columns=["Name", "Email", "Rating", "Comments"])
        if os.path.exists("feedback.csv"):
            existing = pd.read_csv("feedback.csv")
            feedback = pd.concat([existing, feedback], ignore_index=True)
        feedback.to_csv("feedback.csv", index=False)

        # Generate certificate
        cert_dir = "certificates"
        os.makedirs(cert_dir, exist_ok=True)
        cert_path = os.path.join(cert_dir, f"{name.replace(' ', '_')}.png")
        generate_certificate(name, cert_path)

        # Send certificate via email
        try:
            send_certificate(email, name, cert_path)
            st.success("✅ Feedback submitted and certificate sent to your email!")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")
