🛡️ AI-Powered Phishing Email Detector

A cybersecurity tool that detects phishing emails using Machine Learning + AI (Ollama optional).
It provides a Flask Web Dashboard to upload .eml files, analyze risks, and visualize phishing trends.

🚀 Features

📩 Upload .eml files via web dashboard

🔍 Extract & analyze email headers + body text

🤖 AI-powered phishing detection (with adaptive training)

📊 Dashboard with risk scores, trends, and history

🔒 Local-only (can be tunneled with ngrok if needed)

🛠 Extendable with Ollama for advanced AI insights

📂 Project Structure
.
├── main.py           # Flask app (dashboard + ML logic)
├── requirements.txt  # Dependencies
├── .gitignore        # Ignore unnecessary files
├── LICENSE           # MIT License
└── sample_emails/    # Example emails for testing

⚡ Installation

Clone the repo:

git clone https://github.com/<your-username>/phishing-detector.git
cd phishing-detector


Create a virtual environment:

python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows


Install dependencies:

pip install -r requirements.txt

▶️ Usage

Run the web dashboard:

python3 main.py


Then open http://127.0.0.1:5000
.

Upload an .eml file and view the phishing risk score.

📊 Example Output

✅ Safe email → Risk Score: Low

⚠️ Suspicious email → Risk Score: Medium

🚨 Phishing email → Risk Score: High

Dashboard also shows:

Risk score per email

Phishing vs Safe trend chart

Email analysis history

🔮 Future Improvements

🌐 Ngrok auto-tunneling for remote access

📬 Gmail/Outlook integration for live scanning

🧠 Smarter AI training with continuous feedback

📱 Mobile-friendly dashboard

📜 License

MIT License © 2025 Sahil
