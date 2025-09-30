from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Add a test user manually
    test_user = User(username="demo_user2", password_hash=generate_password_hash("demo_pass"))
    db.session.add(test_user)
    db.session.commit()

    # Print all users to confirm
    users = User.query.all()
    for u in users:
        print(u.id, u.username, u.password_hash)