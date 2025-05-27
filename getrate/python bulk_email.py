import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP Configuration
smtp_server = "smtp.office365.com"
smtp_port = 587
username = "no-reply@sinewave.in"
password = "mcwxnfkqhthkbnyw"  # ⚠️ Replace with env variable or secure storage in production

# Email Content
subject = "Your Subject Here"
html_template = """
<html>
<body>
    <p>Dear {name},</p>
    <p>This is a test email sent using Python and Office365 SMTP.</p>
    <p>Best regards,<br>Your Company</p>
</body>
</html>
"""

# Load Excel file from Downloads folder
excel_path = r"C:\Users\Sinewave#2022\Downloads\customers.xlsx"
try:
    df = pd.read_excel(excel_path)
except FileNotFoundError:
    print(f"❌ Excel file not found at: {excel_path}")
    exit(1)

# Setup SMTP session
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)
except Exception as e:
    print(f"❌ SMTP connection/login failed: {e}")
    exit(1)

# Send emails
for index, row in df.iterrows():
    name = row['Name']
    recipient = row['Email']

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = username
    msg["To"] = recipient

    body = html_template.format(name=name)
    msg.attach(MIMEText(body, "html"))

    try:
        server.sendmail(username, recipient, msg.as_string())
        print(f"✅ Email sent to {recipient}")
    except Exception as e:
        print(f"❌ Failed to send email to {recipient}: {e}")

server.quit()
print("✅ All emails processed.")
