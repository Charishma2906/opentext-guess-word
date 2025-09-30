from app import app
from models import User
from extensions import db

with app.app_context():
    users = User.query.all()
    for u in users:
        print(u.id, u.username)
