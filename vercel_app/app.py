from flask import Flask, request, render_template
import os
import zipfile
import subprocess
import yagmail
from dotenv import load_dotenv

# ----------------------------
# Load ENV variables
# ----------------------------
load_dotenv()

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# ----------------------------
# Flask App
# ----------------------------
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROGRAM1_PATH = os.path.join(BASE_DIR, "102303480.py")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ----------------------------
# Home Page
# ----------------------------
@app.route('/')
def home():
    return render_template("index.html")

# ----------------------------
# Send Email
# ----------------------------
def send_email(receiver, file_path):
    try:
        if not EMAIL or not APP_PASSWORD:
            return "Error: Email credentials not set"

        if "@" not in receiver:
            return "Error: Invalid email"

        if not os.path.exists(file_path):
            return "Error: File not found"

        yag = yagmail.SMTP(EMAIL, APP_PASSWORD)

        yag.send(
            to=receiver,
            subject="🎧 Your Mashup File",
            contents="Your mashup is ready! 🎶",
            attachments=file_path
        )

        return "Email sent successfully!"

    except Exception as e:
        return f"Email error: {str(e)}"

# ----------------------------
# Process Route
# ----------------------------
@app.route('/process', methods=['POST'])
def process():
    try:
        singer = request.form['singer']
        num = request.form['num']
        duration = request.form['duration']
        email = request.form['email']

        # Validation
        if int(num) <= 10:
            return "Error: Number of videos must be > 10"

        if int(duration) <= 20:
            return "Error: Duration must be > 20 seconds"

        output_file = "mashup.mp3"

        # ----------------------------
        # Run Program 1
        # ----------------------------
        cmd = [
            "python",
            PROGRAM1_PATH,
            singer,
            num,
            duration,
            output_file
        ]

        print("Running mashup script...")
        subprocess.run(cmd, check=True)

        # ----------------------------
        # Check output file
        # ----------------------------
        output_path = os.path.join(OUTPUT_FOLDER, output_file)

        if not os.path.exists(output_path):
            return "Error: Mashup file not generated"

        # ----------------------------
        # Create ZIP
        # ----------------------------
        zip_path = os.path.join(OUTPUT_FOLDER, "mashup.zip")

        with zipfile.ZipFile(zip_path, 'w') as z:
            z.write(output_path, output_file)

        # ----------------------------
        # Send Email
        # ----------------------------
        result = send_email(email, zip_path)

        return result

    except Exception as e:
        return f"Error: {str(e)}"

# ----------------------------
# Vercel Entry Point
# ----------------------------
app = app
