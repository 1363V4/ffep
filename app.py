from flask import Flask, flash, redirect, request, render_template, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash, safe_join
import json
import os
from pathlib import Path
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

devdir = Path(__file__).parent
datadir_people = devdir / "data" / "people"
datadir_games = devdir / "data" / "games"
datadir_temp = devdir / "data" / "temp"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pwd']
        file = safe_join(datadir_people, username + ".json")
        if file:
            file = Path(file)
            if file.exists():
                with open(file) as f:
                    data = json.load(f)
                if check_password_hash(data['hash'], password):
                    session['username'] = username 
                    flash('You were successfully logged in')
                    return redirect(url_for('dashboard'))
    flash("Login failed")
    return redirect(url_for('home'))

@app.route('/apply', methods=['POST'])
def apply():
    if request.method == 'POST':
        data = {
            'username': request.form['username'],
            'password': request.form['pwd'],
            'repeat_password': request.form['repeat-pwd'],
            'reason': request.form['reason'],
            'hear_about': request.form['hear-about']
        }
        current_time = str(int(datetime.now().timestamp()))
        dest = datadir_temp / current_time
        dest = dest.with_suffix(".json")
        with open(dest, 'w') as f:
            json.dump(data, f, indent=4)
        flash('Message sent')
        return redirect(url_for('join'))
    flash("Not logged in")
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/join')
def join():
    return render_template('join.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html')
    flash("Not logged in")
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'username' in session:
        with open(datadir_people / f"{session['username']}.json") as f:
            user = json.load(f)
            user['username'] = session['username']
        return render_template('profile.html', user=user)
    flash("Not logged in")
    return redirect(url_for('home'))

@app.route('/games')
def games():
    games = []
    for game_json in datadir_games.iterdir():
        with open(game_json) as f:
            game = json.load(f)
        games += [game]
    return render_template('games.html', games=games)

@app.route('/snitch')
def snitch():
    snitches = []
    for snitch_json in datadir_temp.iterdir():
        with open(snitch_json) as f:
            snitch = json.load(f)
        snitches += [snitch]
    return render_template('snitch.html', snitches=snitches)

if __name__ == '__main__':
    app.run(debug=True)