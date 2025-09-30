from extensions import db
from flask_login import UserMixin
from datetime import date
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="player")  # "player" or "admin"
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(10), nullable=False)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'), nullable=False)
    status = db.Column(db.String(20), default="active")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # <-- ADD THIS
    played_on = db.Column(db.Date, default=date.today)

    # ✅ Add relationship so game.word works
    word = db.relationship('Word', backref='games')
    user = db.relationship('User', backref='games')

class Guess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    guess_word = db.Column(db.String(10), nullable=False)
    result_json = db.Column(db.Text, nullable=False)
    guess_order = db.Column(db.Integer, nullable=False)
    correct = db.Column(db.Boolean, default=False) 
    
    game = db.relationship('Game', backref='guesses')
