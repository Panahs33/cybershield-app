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
        email = request.form['email']
        result = analyze_email(email)
    return render_template('analyze.html', result=result)

def analyze_email(text):
    suspicious_keywords = [
        'urgent', 'verify your account', 'click here', 'login now',
        'wire transfer', 'password expired', 'unusual activity',
        'account locked', 'confirm billing', 'security alert',
        'reactivate', 'suspicious', 'reset password', 'payment required'
    ]
    score = sum(1 for word in suspicious_keywords if word in text.lower())
    if score >= 3:
        return "❌ This message contains multiple phishing red flags."
    elif score >= 1:
        return "⚠️ Slightly suspicious. Review carefully."
    else:
        return "✅ No obvious phishing signs detected."

# === START APP ===
if __name__ == '__main__':
    app.run(debug=True)