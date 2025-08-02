import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import smtplib
from email.message import EmailMessage
import os
from email_validator import validate_email, EmailNotValidError

# Email credentials (use environment variables for safety)
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"

CERT_TEMPLATE_PATH = "certificate_template.jpg"  # Use your own template
FONT_PATH = "arial.ttf"  # Path to a TTF font file

# Feedback Form
st.title("🔁 Feedback Form + Certificate")

name = st.text_input("Full Name")
email = st.text_input("Email")
feedback = st.text_area("Your Feedback")

if st.button("Submit Feedback & Get Certificate"):
    if not name or not email:
        st.warning("Please enter your name and email.")
    else:
        try:
            valid = validate_email(email)
            email = valid.email

            # Generate certificate image
            cert_img = Image.open(CERT_TEMPLATE_PATH)
            draw = ImageDraw.Draw(cert_img)
            font = ImageFont.truetype(FONT_PATH, 60)

            # Customize coordinates (depends on your template)
            draw.text((700, 800), name, font=font, fill="black")

            cert_filename = f"{name.replace(' ', '_')}_certificate.jpg"
            cert_img.save(cert_filename)

            # Convert to PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.image(cert_filename, x=0, y=0, w=210, h=297)  # A4 size
            pdf_filename = cert_filename.replace('.jpg', '.pdf')
            pdf.output(pdf_filename)

            # Email the certificate
            msg = EmailMessage()
            msg['Subject'] = 'Your Certificate from Excelrate!'
            msg['From'] = EMAIL_SENDER
            msg['To'] = email
            msg.set_content(f"Dear {name},\n\nThank you for your feedback!\nFind your certificate attached.\n\nRegards,\nExcelrate Team")

            with open(pdf_filename, 'rb') as f:
                file_data = f.read()
                msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=pdf_filename)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(msg)

            st.success("✅ Certificate sent to your email!")

            # Clean up files
            os.remove(cert_filename)
            os.remove(pdf_filename)

        except EmailNotValidError as e:
            st.error(f"Invalid Email: {e}")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
