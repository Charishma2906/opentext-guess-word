from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Game, Guess, Word
from datetime import datetime, date
import re
import json
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key_here"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guessword.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ---------------- HOME PAGE ----------------
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role != "admin":
            return redirect(url_for("player_dashboard"))
        
    return render_template('index.html')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not re.match(r'^[A-Za-z]{5,}$', username):
            flash("Username must be at least 5 letters.", "danger")
            return render_template('register.html')

        if not re.match(r'^(?=.*[0-9])(?=.*[$%@*])[A-Za-z0-9$%@*]{5,}$', password):
            flash("Password must have 5+ chars, include number & special char ($,% ,*,@).", "danger")
            return render_template('register.html')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "danger")
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(username=username, password_hash=hashed_pw, role="player")
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    role = request.args.get("role", "player")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            # Redirect player to dashboard instead of landing page
            if user.role == "admin" or role == "admin":
                return redirect(url_for('daily_report'))
            return redirect(url_for('player_dashboard'))
        else:
            flash("Invalid username or password!", "danger")
    return render_template('login.html', role=role)

# ---------------- PLAYER DASHBOARD ----------------
@app.route('/player/dashboard')
@login_required
def player_dashboard():
    if current_user.role == "admin":  # admin should not land here
        return redirect(url_for("daily_report"))

    active_game = Game.query.filter_by(user_id=current_user.id, status="active").first()
    return render_template("player_dashboard.html", has_active_game=bool(active_game))

@app.route('/player')
def player_home():
    if current_user.is_authenticated and current_user.role == "player":
        return redirect(url_for('player_dashboard'))  # if already logged in, go straight to dashboard
    return render_template("player_home.html")  # choose login/register
# ---------------- LOGOUT ----------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('index'))

# ---------------- START GAME ----------------
@app.route("/start-game")
@login_required
def start_game():
    if current_user.role == "admin":
        flash("Admins cannot play games.", "danger")
        return redirect(url_for("daily_report"))

    active_game = Game.query.filter_by(user_id=current_user.id, status="active").first()
    if active_game:
        return redirect(url_for("play"))

    today_games = Game.query.filter(
        Game.user_id == current_user.id,
        Game.timestamp >= date.today()
    ).count()

    if today_games >= 3:
        flash("You can only play 3 games per day!", "warning")
        return redirect(url_for("player_dashboard"))

    random_word = Word.query.order_by(db.func.random()).first()
    if not random_word:
        flash("No words available. Please ask admin to add words.", "danger")
        return redirect(url_for("player_dashboard"))

    new_game = Game(user_id=current_user.id, word_id=random_word.id, status="active", timestamp=datetime.now())
    db.session.add(new_game)
    db.session.commit()

    return redirect(url_for("play"))

# ---------------- PAUSE/RESUME/RESTART ----------------
@app.route('/pause-game')
@login_required
def pause_game():
    game = Game.query.filter_by(user_id=current_user.id, status="active").first()
    if game:
        game.status = "paused"
        db.session.commit()
    return render_template('pause.html')

@app.route('/resume-game')
@login_required
def resume_game():
    game = Game.query.filter_by(user_id=current_user.id, status="paused").first()
    if game:
        game.status = "active"
        db.session.commit()
        return redirect(url_for("play"))
    flash("No paused game found.", "warning")
    return redirect(url_for("player_dashboard"))

@app.route('/restart-game')
@login_required
def restart_game():
    today_games = Game.query.filter(
        Game.user_id == current_user.id,
        Game.timestamp >= date.today()
    ).count()
    if today_games >= 3:
        flash("You can only play 3 games per day!", "danger")
        return redirect(url_for('player_dashboard'))

    random_word = Word.query.order_by(db.func.random()).first()
    if not random_word:
        flash("No words available. Please ask admin to add words.", "danger")
        return redirect(url_for("player_dashboard"))

    new_game = Game(user_id=current_user.id, word_id=random_word.id, status="active", timestamp=datetime.now())
    db.session.add(new_game)
    db.session.commit()
    return redirect(url_for("play"))

# ---------------- PLAY GAME ----------------
@app.route('/play', methods=['GET', 'POST'])
@login_required
def play():
    game = Game.query.filter_by(user_id=current_user.id, status="active").first()

    if not game:
        flash("No active game found. Please start a new game.", "warning")
        return redirect(url_for('player_dashboard'))

    guesses = Guess.query.filter_by(game_id=game.id).order_by(Guess.guess_order).all()
    popup_message = None
    game_over = False

    if request.method == 'POST':
        guess_word = request.form['guess'].upper()
        result_colors = evaluate_guess(guess_word, get_word_text(game.word_id))

        new_guess = Guess(
            game_id=game.id,
            guess_word=guess_word,
            result_json=json.dumps(result_colors),
            guess_order=len(guesses) + 1
        )

        if guess_word == get_word_text(game.word_id):
            new_guess.correct = True
            game.status = "won"
            popup_message = "🎉 Congratulations! You guessed the word correctly!"
            game_over = True
            
        elif len(guesses) >= 4:
            game.status = "lost"
            popup_message = f"❌ Better luck next time! The word was {get_word_text(game.word_id)}."
            game_over = True
            

        db.session.add(new_guess)
        db.session.commit()

    guesses = Guess.query.filter_by(game_id=game.id).order_by(Guess.guess_order).all()
    guesses_with_colors = [{"word": g.guess_word, "colors": json.loads(g.result_json)} for g in guesses]

    return render_template('play.html',
                           guesses=guesses_with_colors,
                           popup_message=popup_message,
                           game_over=game_over)

# ---------------- UTILITIES ----------------
def get_word_text(word_id):
    word = Word.query.filter_by(id=word_id).first()
    return word.word if word else ""

def evaluate_guess(guess, target):
    colors = []
    for i, letter in enumerate(guess):
        if i < len(target) and letter == target[i]:
            colors.append("green")
        elif letter in target:
            colors.append("orange")
        else:
            colors.append("grey")
    return colors

# ---------------- ADMIN REPORTS ----------------
@app.route('/admin/report/daily')
@login_required
def daily_report():
    if current_user.role != "admin":
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('player_dashboard'))

    games = Game.query.all()
    daily_data = {}
    for game in games:
        date_key = game.timestamp.date()
        if date_key not in daily_data:
            daily_data[date_key] = {"users": set(), "correct": 0}
        daily_data[date_key]["users"].add(game.user_id)
        if game.status == "won":
            daily_data[date_key]["correct"] += 1

    report_list = []
    for date_key, data in sorted(daily_data.items(), key=lambda x: x[0], reverse=True):
        user_details = [
            {"id": uid, "username": User.query.get(uid).username}
            for uid in data["users"]
            if User.query.get(uid).role != "admin"  # hide admin from reports
        ]
        report_list.append({
            "date": date_key,
            "users": user_details,
            "correct": data["correct"]
        })

    return render_template("daily_report.html", report_list=report_list)

@app.route('/admin/report/user/<int:user_id>')
@login_required
def user_report(user_id):
    if current_user.role != "admin":
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('player_dashboard'))

    games = Game.query.filter_by(user_id=user_id).all()
    report_data = {}
    for game in games:
        date_key = game.timestamp.date()
        if date_key not in report_data:
            report_data[date_key] = {"words_tried": 0, "correct": 0}
        report_data[date_key]["words_tried"] += 1
        if game.status == "won":
            report_data[date_key]["correct"] += 1

    report_list = [
        {"date": date, "words_tried": data["words_tried"], "correct": data["correct"]}
        for date, data in sorted(report_data.items(), key=lambda x: x[0], reverse=True)
    ]

    return render_template("user_report.html",
                           report_list=report_list,
                           username=User.query.get(user_id).username)

@app.route("/admin/all-guesses")
@login_required
def all_guesses():
    if current_user.role != "admin":
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('player_dashboard'))

    games = Game.query.order_by(Game.timestamp.desc()).all()
    return render_template("all_guesses.html", games=games)

if __name__ == "__main__":
    app.run(debug=True)
