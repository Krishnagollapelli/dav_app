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

# GitHub image URL for the certificate template
CERT_TEMPLATE_URL = "https://raw.githubusercontent.com/krishnagollapelli/excelrate-cert-app/main/assets/certificate_template.jpg"

# Font file must be present locally
FONT_PATH = "arial.ttf"  # You can upload this file in your working directory
FONT_SIZE = 60
TEXT_POSITION = (700, 800)  # Adjust based on your certificate layout
# ----------------------------------------------------------

st.title("🔁 Feedback Form + Certificate Generator")

name = st.text_input("Full Name")
email = st.text_input("Email")
feedback = st.text_area("Your Feedback")

if st.button("Submit Feedback & Get Certificate"):
    if not name or not email:
        st.warning("Please enter your name and email.")
    else:
        try:
            # Validate email format
            valid = validate_email(email)
            email = valid.email

            # Load certificate template from GitHub URL
            response = requests.get(CERT_TEMPLATE_URL)
            cert_img = Image.open(BytesIO(response.content)).convert("RGB")

            # Draw name on certificate
            draw = ImageDraw.Draw(cert_img)
            font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
            draw.text(TEXT_POSITION, name, font=font, fill="black")

            # Save as JPG
            cert_filename = f"{name.replace(' ', '_')}_certificate.jpg"
            cert_img.save(cert_filename)

            # Convert to PDF
            pdf_filename = cert_filename.replace(".jpg", ".pdf")
            pdf = FPDF()
            pdf.add_page()
            pdf.image(cert_filename, x=0, y=0, w=210, h=297)  # A4 Size
            pdf.output(pdf_filename)

            # Compose Email
            msg = EmailMessage()
            msg['Subject'] = 'Your Certificate from Excelrate!'
            msg['From'] = EMAIL_SENDER
            msg['To'] = email
            msg.set_content(
                f"Dear {name},\n\nThank you for your feedback!\nPlease find your certificate attached.\n\nRegards,\nExcelrate Team"
            )

            # Attach PDF
            with open(pdf_filename, 'rb') as f:
                msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=pdf_filename)

            # Send Email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(msg)

            st.success("✅ Certificate sent to your email!")

            # Clean up files
            os.remove(cert_filename)
            os.remove(pdf_filename)

        except EmailNotValidError as e:
            st.error(f"❌ Invalid Email: {e}")
        except Exception as e:
            st.error(f"🚨 Something went wrong: {e}")
