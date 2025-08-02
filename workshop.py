from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_ID = os.getenv("EMAIL_ID")
EMAIL_PASS = os.getenv("EMAIL_PASS")

FEEDBACK_CSV = "feedback.csv"
CERTIFICATE_DIR = "certificates"

def generate_certificate(name, cert_path):
    if os.path.exists("certificate_template.png"):
        template = Image.open("certificate_template.png")
    else:
        template = Image.new("RGB", (1200, 800), color=(255, 255, 255))

    draw = ImageDraw.Draw(template)
    font = ImageFont.truetype("arial.ttf", 60)
    draw.text((300, 350), "Certificate of Participation", font=font, fill="black")
    draw.text((300, 450), f"Awarded to: {name}", font=font, fill="black")
    template.save(cert_path)

def send_certificate(email_to, name, cert_path):
    msg = EmailMessage()
    msg['Subject'] = "🎉 Your Workshop Certificate - Excelrate"
    msg['From'] = EMAIL_ID
    msg['To'] = email_to
    msg.set_content(
        f"Dear {name},\n\nThanks for attending Excelrate Workshop!\nPlease find your certificate attached.\n\nRegards,\nTeam Excelrate"
    )
    with open(cert_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(cert_path)
        msg.add_attachment(file_data, maintype='image', subtype='png', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ID, EMAIL_PASS)
        smtp.send_message(msg)

def submit_feedback(name, email, rating, comments):
    # Save feedback
    new_entry = pd.DataFrame([[name, email, rating, comments]],
                             columns=["Name", "Email", "Rating", "Comments"])
    if os.path.exists(FEEDBACK_CSV):
        existing = pd.read_csv(FEEDBACK_CSV)
        df = pd.concat([existing, new_entry], ignore_index=True)
    else:
        df = new_entry
    df.to_csv(FEEDBACK_CSV, index=False)

    # Generate certificate
    os.makedirs(CERTIFICATE_DIR, exist_ok=True)
    cert_path = os.path.join(CERTIFICATE_DIR, f"{name.replace(' ', '_')}.png")
    generate_certificate(name, cert_path)

    # Send certificate email
    send_certificate(email, name, cert_path)

    print(f"Feedback submitted for {name} and certificate sent to {email}.")

def view_feedback():
    if not os.path.exists(FEEDBACK_CSV):
        print("No feedback available.")
        return
    df = pd.read_csv(FEEDBACK_CSV)
    print(df)

def get_certificate_path(name):
    cert_path = os.path.join(CERTIFICATE_DIR, f"{name.replace(' ', '_')}.png")
    if os.path.exists(cert_path):
        print(f"Certificate path: {cert_path}")
    else:
        print("Certificate not found.")

# Example usage (can replace this with any UI or CLI integration)
if __name__ == "__main__":
    print("1. Submit feedback")
    print("2. View all feedback (admin)")
    print("3. Get certificate path (admin)")
    choice = input("Enter option number: ")

    if choice == "1":
        n = input("Name: ")
        e = input("Email: ")
        r = int(input("Rating (1-5): "))
        c = input("Comments: ")
        submit_feedback(n, e, r, c)
    elif choice == "2":
        view_feedback()
    elif choice == "3":
        n = input("Enter name to get certificate path: ")
        get_certificate_path(n)
    else:
        print("Invalid option.")
