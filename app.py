from flask import Flask, jsonify, render_template, request, session
import json

app = Flask(__name__)
app.secret_key = 'supersecret'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/learn')
def learn():
    facts = [
    "⚠️ Over 90% of cyber attacks begin with phishing, making it the #1 threat vector.",
    "🔍 Always inspect the full URL — attackers often mimic domains using subtle typos.",
    "🔐 Just because a site uses HTTPS doesn't mean it's safe. Phishing sites can use HTTPS too.",
    "📬 Generic greetings like 'Dear Customer' indicate bulk email phishing tactics.",
    "🧠 Phishing emails often exploit urgency and fear to trick victims into clicking.",
    "📈 Spear phishing is a targeted attack that uses your personal info against you.",
    "🤖 AI-based phishing detectors analyze language patterns, timing, and sender behavior.",
    "📎 Never open attachments from unknown sources — malware is often hidden in .exe or .zip files.",
    "💼 Business Email Compromise (BEC) targets executives and can lead to large-scale fraud.",
    "🔄 Phishing emails are often sent from lookalike domains like amaz0n.com or paypa1.com.",
    "🚫 Don't trust emails asking for urgent wire transfers or login verification without confirmation.",
    "📱 Phishing isn't just on email — it can also come via SMS (smishing) or phone calls (vishing).",
    "🎓 Security awareness training reduces phishing click rates by over 70% in educated organizations.",
    "📊 Attackers often research social media and company org charts to personalize phishing attacks.",
    "🛑 If in doubt — stop and report. Reporting phishing helps protect the whole network."
]
    return render_template('learn.html', facts=facts)

@app.route('/select')
def select_level():
    return render_template('quiz_select.html')

@app.route('/quiz/<level>')
def quiz(level):
    session['score'] = 0
    return render_template('quiz.html', level=level)

import random

@app.route('/get_questions/<level>')
def get_questions(level):
    with open('static/questions.json') as f:
        data = json.load(f)
    questions = data.get(level, [])
    random.shuffle(questions)

    
    for q in questions:
        if 'options' in q:
            random.shuffle(q['options'])

    return jsonify(questions)
@app.route('/save_score', methods=['POST'])
def save_score():
    session['score'] = request.json.get('score', 0)
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True)