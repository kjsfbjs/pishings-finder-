import os
import re
import email
import joblib
import pandas as pd
from flask import Flask, render_template_string, request, redirect, url_for
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Storage paths
BASE_DIR = os.path.expanduser("~/.phishguard")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DATASET_FILE = os.path.join(BASE_DIR, "dataset.csv")
MODEL_FILE = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_FILE = os.path.join(BASE_DIR, "vectorizer.pkl")

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Flask
app = Flask(__name__)

# Simple HTML template with Bootstrap + Chart.js
template = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PhishGuard Dashboard</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="bg-dark text-light">
<div class="container py-4">
  <h1 class="mb-4">📧 PhishGuard Dashboard</h1>
  <form action="/upload" method="post" enctype="multipart/form-data" class="mb-3">
    <div class="input-group">
      <input type="file" class="form-control" name="email_file" required>
      <button class="btn btn-primary" type="submit">Analyze</button>
    </div>
  </form>

  {% if result %}
  <div class="card mb-4">
    <div class="card-body">
      <h5>Result: <span class="badge bg-{{ 'danger' if result['label']=='phishing' else 'success' }}">{{ result['label'] }}</span></h5>
      <p>Risk Score: {{ result['score'] }}</p>
      <p><b>Explanation:</b> {{ result['explanation'] }}</p>
    </div>
  </div>
  {% endif %}

  <h3>History</h3>
  <table class="table table-dark table-striped">
    <thead><tr><th>Filename</th><th>Label</th><th>Score</th></tr></thead>
    <tbody>
    {% for row in history %}
      <tr>
        <td>{{ row['filename'] }}</td>
        <td><span class="badge bg-{{ 'danger' if row['label']=='phishing' else 'success' }}">{{ row['label'] }}</span></td>
        <td>{{ row['score'] }}</td>
      </tr>
    {% endfor %}
    </tbody>
  </table>

  <canvas id="chart" height="100"></canvas>
  <script>
    const ctx = document.getElementById('chart');
    const chart = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ['Phishing','Safe'],
        datasets: [{
          data: [{{ phish_count }}, {{ safe_count }}],
          backgroundColor: ['#dc3545','#198754']
        }]
      }
    });
  </script>
</div>
</body>
</html>
"""

# ML setup
def load_or_train():
    if os.path.exists(MODEL_FILE) and os.path.exists(VECTORIZER_FILE):
        clf = joblib.load(MODEL_FILE)
        vec = joblib.load(VECTORIZER_FILE)
        return clf, vec
    return LogisticRegression(), TfidfVectorizer()

clf, vec = load_or_train()

# Heuristic + ML analyzer
def analyze_email(file_path):
    with open(file_path, "r", errors="ignore") as f:
        msg = email.message_from_file(f)
    subject = msg["subject"] or ""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body += part.get_payload(decode=True).decode(errors="ignore")
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")

    text = subject + " " + body

    heuristics = 0
    if re.search(r"http[s]?://[\w\.-]+", text):
        heuristics += 0.3
    if re.search(r"verify|urgent|password|bank|login", text, re.I):
        heuristics += 0.3

    if os.path.exists(MODEL_FILE):
        X = vec.transform([text])
        ml_score = clf.predict_proba(X)[0][1]
    else:
        ml_score = 0.5

    score = round((heuristics + ml_score) / 2, 2)
    label = "phishing" if score > 0.5 else "safe"

    return {"label": label, "score": score, "explanation": "AI+heuristics combined analysis"}

# Routes
@app.route("/")
def index():
    history = []
    if os.path.exists(DATASET_FILE):
        df = pd.read_csv(DATASET_FILE)
        history = df.to_dict(orient="records")
    phish_count = sum(1 for h in history if h['label'] == 'phishing')
    safe_count = sum(1 for h in history if h['label'] == 'safe')
    return render_template_string(template, result=None, history=history[-10:], phish_count=phish_count, safe_count=safe_count)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['email_file']
    path = os.path.join(UPLOAD_DIR, file.filename)
    file.save(path)
    result = analyze_email(path)

    row = {"filename": file.filename, "label": result['label'], "score": result['score']}
    df = pd.DataFrame([row])
    if os.path.exists(DATASET_FILE):
        df.to_csv(DATASET_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(DATASET_FILE, index=False)

    history = pd.read_csv(DATASET_FILE).to_dict(orient="records")
    phish_count = sum(1 for h in history if h['label'] == 'phishing')
    safe_count = sum(1 for h in history if h['label'] == 'safe')
    return render_template_string(template, result=result, history=history[-10:], phish_count=phish_count, safe_count=safe_count)

if __name__ == "__main__":
    app.run(debug=True)
