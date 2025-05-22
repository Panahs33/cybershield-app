from flask import Flask, render_template, request, jsonify, session
import json
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session handling

# === ROUTES ===

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/learn')
def learn():
    facts = [
        "Phishing emails often use urgent language to pressure you.",
        "Hovering over links shows the true destination.",
        "AI tools like PhishHaven detect subtle behavior anomalies.",
        "HTTPS alone doesn't guarantee a site is safe.",
        "Generic greetings like 'Dear Customer' are red flags.",
        "Misspelled domains (e.g. paypa1.com) are suspicious.",
        "Unsolicited attachments may contain malware.",
        "Legitimate companies rarely request sensitive info via email.",
        "Phishing sites often look pixel-perfect to mimic real ones.",
        "AI can detect patterns human reviewers miss.",
        "Look out for slight domain name variations (like amaz0n.com).",
        "Urgent subject lines are commonly used in phishing.",
        "Don't trust emails asking to reset your password unexpectedly.",
        "AI can learn what a user's normal behavior looks like.",
        "Phishing costs businesses billions yearly in data loss."
    ]
    return render_template('learn.html', facts=facts)

@app.route('/select')
def select_level():
    return render_template('quiz_select.html')

@app.route('/quiz/<level>')
def quiz(level):
    return render_template('quiz.html', level=level)

@app.route('/get_questions/<level>')
def get_questions(level):
    with open('static/questions.json') as f:
        data = json.load(f)
    questions = data.get(level, [])
    for q in questions:
        random.shuffle(q["options"])
    random.shuffle(questions)
    return jsonify(questions)

@app.route('/save_score', methods=['POST'])
def save_score():
    session['score'] = request.json.get('score', 0)
    return ('', 204)

@app.route('/get_score')
def get_score():
    return jsonify({'score': session.get('score', 0)})

# === NEW: PHISHING EMAIL CHECKER ===

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    result = None
    if request.method == 'POST':
        email_text = request.form['email']
        headers = request.form.get('headers', '')
        result = analyze_email(email_text, headers)
    return render_template('analyze.html', result=result)

def analyze_email(text, headers=""):
    import re
    score = 0
    issues = []

    text = text.lower()

    # --- 1. Suspicious Keywords ---
    keywords = [
        "urgent", "verify your account", "click here", "login now", "update payment",
        "account locked", "unusual activity", "security alert", "reset password", "wire transfer"
    ]
    for kw in keywords:
        if kw in text:
            score += 1
            issues.append(f"Keyword match: <b>{kw}</b>")

    # --- 2. Threats ---
    threats = [
        "your account will be closed", "final notice", "act immediately", "will be terminated"
    ]
    for t in threats:
        if t in text:
            score += 1
            issues.append(f"Threatening tone: <b>{t}</b>")

    # --- 3. Suspicious Links ---
    links = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    for link in links:
        if "bit.ly" in link or "tinyurl" in link or re.search(r'\d+\.\d+\.\d+\.\d+', link):
            score += 1
            issues.append(f"Suspicious link: <code>{link}</code>")

    # --- 4. Generic Greetings ---
    if "dear customer" in text or "dear user" in text:
        score += 1
        issues.append("Generic greeting detected")

    # === HEADER ANALYSIS ===
    headers = headers.lower()

    if headers:
        if "reply-to:" in headers and "from:" in headers:
            from_match = re.search(r"from:\s*(.+)", headers)
            reply_match = re.search(r"reply-to:\s*(.+)", headers)
            if from_match and reply_match and from_match.group(1) != reply_match.group(1):
                score += 1
                issues.append(f"<b>Mismatch</b> between <code>From</code> and <code>Reply-To</code> addresses")

        if "spf=fail" in headers or "dmarc=fail" in headers or "dkim=fail" in headers:
            score += 1
            issues.append("Email failed SPF/DKIM/DMARC checks")

        if "received:" in headers:
            received_count = headers.count("received:")
            if received_count > 5:
                issues.append("Multiple 'Received:' lines — may be relayed")
            if "unknown" in headers or "dynamic" in headers:
                score += 1
                issues.append("Header shows possibly spoofed server (unknown/dynamic)")

    # === RESULT FORMAT ===
    if score >= 4:
        status = "❌ High phishing risk!"
    elif score >= 2:
        status = "⚠️ Suspicious content found."
    else:
        status = "✅ No major phishing signs detected."

    return f"<strong>Status</strong><br> • " + "<br>• ".join(issues) if issues else status

# === START APP ===
if __name__ == '__main__':
    app.run(debug=True)