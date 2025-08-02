
from pydantic import BaseModel, EmailStr
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class Feedback(BaseModel):
    name: str
    email: EmailStr
    rating: int
    comments: str = ""

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

@app.post("/submit-feedback")
async def submit_feedback(feedback: Feedback):
    # Save feedback to CSV
    new_entry = pd.DataFrame([[feedback.name, feedback.email, feedback.rating, feedback.comments]],
                             columns=["Name", "Email", "Rating", "Comments"])
    if os.path.exists("feedback.csv"):
        existing = pd.read_csv("feedback.csv")
        df = pd.concat([existing, new_entry], ignore_index=True)
    else:
        df = new_entry
    df.to_csv("feedback.csv", index=False)

    # Generate certificate
    cert_dir = "certificates"
    os.makedirs(cert_dir, exist_ok=True)
    cert_path = os.path.join(cert_dir, f"{feedback.name.replace(' ', '_')}.png")
    generate_certificate(feedback.name, cert_path)

    # Send email
    try:
        send_certificate(feedback.email, feedback.name, cert_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {"message": "Feedback received and certificate sent to your email."}
