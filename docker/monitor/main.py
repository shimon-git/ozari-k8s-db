import yaml
import smtplib
import ssl
import logging
from flask import Flask, request, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load configuration from YAML file
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Threshold for alerting (set in YAML or use default 80%)
#THRESHOLD = config.get("threshold_percentage", 80)
THRESHOLD = config.get("threshold", {}).get("disk_usage", 80)

# Function to send email
def send_email(subject, body):
    smtp_conf = config["smtp"]
    sender_email = smtp_conf["sender"]
    recipients = config["recipients"]

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_conf["host"], smtp_conf["port"], context=context) as server:
            if smtp_conf.get("username") and smtp_conf.get("password"):
                server.login(smtp_conf["username"], smtp_conf["password"])
            server.sendmail(sender_email, recipients, msg.as_string())
        logging.info("Alert email sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

# API endpoint to receive disk usage alerts
@app.route("/alert", methods=["POST"])
def receive_alert():
    if request.headers.get("monitor") == "disk":
        available_space = request.headers.get("AvailableSpace").replace('G','')
        total_space = request.headers.get("TotalSpace").replace('G','')

        # Validate headers
        if not available_space or not total_space:
            logging.error("Missing AvailableSpace or TotalSpace headers")
            return jsonify({"error": "Missing AvailableSpace or TotalSpace headers"}), 400

        try:
            available_space_gb = float(available_space)
            total_space_gb = float(total_space)
            used_percentage = ((total_space_gb - available_space_gb) / total_space_gb) * 100

            logging.info(f"Disk usage: {used_percentage:.2f}% (Threshold: {THRESHOLD}%)")

            if used_percentage >= THRESHOLD:
                message = (f"🚨 Disk usage alert 🚨\n\n"
                        f"Total Space: {total_space_gb:.2f} GB\n"
                        f"Available Space: {available_space_gb:.2f} GB\n"
                        f"Used: {used_percentage:.2f}% (Threshold: {THRESHOLD}%)")
                send_email("Disk Usage Alert", message)
                return jsonify({"status": "alert_sent"}), 200

            return jsonify({"status": "usage_below_threshold"}), 200

        except ValueError:
            logging.error("Invalid numeric values for AvailableSpace or TotalSpace")
            return jsonify({"error": "Invalid numeric values for AvailableSpace or TotalSpace"}), 400

    return jsonify({"error": "Invalid request"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config["server"]["port"])

