from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

users = {}
user_logs = {}

def calculate_burnout(log):
    score = (
        (10 - log['sleep']/24*10) * 0.2 +
        (10 - log['study']/8*10) * 0.2 +
        (log['screen']/8*10) * 0.15 +
        (10 - log['physical']/2*10) * 0.15 +
        (10 - log['mood']) * 0.15 +
        log['stress'] * 0.15
    )
    percent = max(0, min(100, round(score, 1)))
    return percent

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    logs = user_logs.get(username, [])
    burnout_percents = [log['burnout'] for log in logs]
    dates = [log['date'] for log in logs]
    return render_template('index.html', logs=logs, dates=dates, burnout_percents=burnout_percents)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return "Username already exists"
        users[username] = password
        user_logs[username] = []
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            return "Invalid username or password"
    return render_template('login.html')

@app.route('/add_log', methods=['POST'])
def add_log():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    date = request.form.get('date')
    sleep = float(request.form.get('sleep', 0))
    study = float(request.form.get('study', 0))
    screen = float(request.form.get('screen', 0))
    physical = float(request.form.get('physical', 0))
    mood = int(request.form.get('mood', 5))
    stress = int(request.form.get('stress', 5))
    
    log = {'date': date, 'sleep': sleep, 'study': study, 'screen': screen,
           'physical': physical, 'mood': mood, 'stress': stress}
    log['burnout'] = calculate_burnout(log)
    user_logs[username].append(log)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
