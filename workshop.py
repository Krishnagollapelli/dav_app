from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_ID = os.getenv("EMAIL_ID")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def generate_certificate(name):
    cert_path = f"{name.replace(' ', '_')}_certificate.png"
    if os.path.exists("certificate_template.png"):
        template = Image.open("certificate_template.png")
    else:
        template = Image.new("RGB", (1200, 800), color=(255, 255, 255))

    draw = ImageDraw.Draw(template)
    font = ImageFont.truetype("arial.ttf", 60)
    draw.text((300, 350), "Certificate of Participation", font=font, fill="black")
    draw.text((300, 450), f"Awarded to: {name}", font=font, fill="black")
    template.save(cert_path)
    return cert_path

def send_certificate(email_to, name, cert_path):
    msg = EmailMessage()
    msg["Subject"] = "🎓 Your Certificate - Excelrate Workshop"
    msg["From"] = EMAIL_ID
    msg["To"] = email_to
    msg.set_content(f"Hi {name},\n\nThanks for your feedback! Here's your certificate.\n\nRegards,\nTeam Excelrate")

    with open(cert_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='image', subtype='png', filename=os.path.basename(cert_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ID, EMAIL_PASS)
        smtp.send_message(msg)

def main():
    print("📝 Excelrate Feedback Form\n")
    name = input("Enter your full name: ")
    email = in
