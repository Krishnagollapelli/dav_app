from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_ID = os.getenv("EMAIL_ID")
EMAIL_PASS = os.getenv("EMAIL_PASS")

PARTICIPANTS_CSV = "participants.csv"
FEEDBACK_CSV = "feedback.csv"
CERT_DIR = "certificates"

# ---------------------- Core Functions ---------------------- #

def load_participants():
    if not os.path.exists(PARTICIPANTS_CSV):
        return pd.DataFrame(columns=["Name", "Email", "Allowed", "FeedbackSubmitted"])
    return pd.read_csv(PARTICIPANTS_CSV)

def save_participants(df):
    df.to_csv(PARTICIPANTS_CSV, index=False)

def is_user_allowed(name, email):
    df = load_participants()
    user = df[(df["Name"] == name) & (df["Email"] == email)]
    if user.empty:
        return False, "User not registered"
    if user.iloc[0]["Allowed"].lower() != "yes":
        return False, "You are not allowed to submit feedback"
    if user.iloc[0]["FeedbackSubmitted"].lower() == "yes":
        return False, "Feedback already submitted"
    return True, ""

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
    msg["Subject"] = "🎓 Your Certificate - Excelrate Workshop"
    msg["From"] = EMAIL_ID
    msg["To"] = email_to
    msg.set_content(f"Hi {name},\n\nThanks for your feedback! Here's your certificate.\n\nRegards,\nExcelrate Team")
    with open(cert_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='image', subtype='png', filename=os.path.basename(cert_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ID, EMAIL_PASS)
        smtp.send_message(msg)

def submit_feedback(name, email, rating, comments):
    allowed, reason = is_user_allowed(name, email)
    if not allowed:
        print(f"⛔ {reason}")
        return

    # Save feedback
    feedback_df = pd.DataFrame([[name, email, rating, comments]],
                               columns=["Name", "Email", "Rating", "Comments"])
    if os.path.exists(FEEDBACK_CSV):
        existing = pd.read_csv(FEEDBACK_CSV)
        feedback_df = pd.concat([existing, feedback_df], ignore_index=True)
    feedback_df.to_csv(FEEDBACK_CSV, index=False)

    # Update participant status
    df = load_participants()
    df.loc[(df["Name"] == name) & (df["Email"] == email), "FeedbackSubmitted"] = "yes"
    save_participants(df)

    # Generate & send certificate
    os.makedirs(CERT_DIR, exist_ok=True)
    cert_path = os.path.join(CERT_DIR, f"{name.replace(' ', '_')}.png")
    generate_certificate(name, cert_path)
    send_certificate(email, name, cert_path)
    print(f"✅ Feedback submitted and certificate sent to {email}.")

# ---------------------- Admin Functions ---------------------- #

def add_participant(name, email):
    df = load_participants()
    if ((df["Name"] == name) & (df["Email"] == email)).any():
        print("Participant already exists.")
        return
    new_row = pd.DataFrame([[name, email, "yes", "no"]], columns=["Name", "Email", "Allowed", "FeedbackSubmitted"])
    df = pd.concat([df, new_row], ignore_index=True)
    save_participants(df)
    print(f"✅ Participant {name} added.")

def toggle_access(name, email, status):
    df = load_participants()
    mask = (df["Name"] == name) & (df["Email"] == email)
    if not mask.any():
        print("User not found.")
        return
    df.loc[mask, "Allowed"] = status
    save_participants(df)
    print(f"Access updated for {name} to {status}.")

def view_feedback():
    if not os.path.exists(FEEDBACK_CSV):
        print("No feedback submitted yet.")
        return
    df = pd.read_csv(FEEDBACK_CSV)
    print(df)

# ---------------------- Menu ---------------------- #

def menu():
    while True:
        print("\n1. Submit Feedback (User)")
        print("2. Add Participant (Admin)")
        print("3. Toggle Feedback Access (Admin)")
        print("4. View All Feedback (Admin)")
        print("5. Exit")

        choice = input("Enter option: ")

        if choice == "1":
            name = input("Your Name: ")
            email = input("Your Email: ")
            rating = int(input("Rating (1-5): "))
            comments = input("Comments: ")
            submit_feedback(name, email, rating, comments)

        elif choice == "2":
            name = input("Participant Name: ")
            email = input("Participant Email: ")
            add_participant(name, email)

        elif choice == "3":
            name = input("Participant Name: ")
            email = input("Participant Email: ")
            status = input("Set access to (yes/no): ")
            toggle_access(name, email, status)

        elif choice == "4":
            view_feedback()

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid option. Try again.")
