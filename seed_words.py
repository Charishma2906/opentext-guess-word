from app import app, db
from models import Word

WORDS = [
    "APPLE", "BRICK", "CROWN", "DRIVE", "FLAME",
    "GLASS", "HOUSE", "JUDGE", "KNIFE", "LIGHT",
    "MIGHT", "NIGHT", "OCEAN", "PEACH", "QUEEN",
    "RIVER", "STONE", "TRAIN", "UNITY", "VIVID"
]

with app.app_context():
    db.create_all()  # ensure tables exist
    for w in WORDS:
        if not Word.query.filter_by(word=w).first():
            db.session.add(Word(word=w))
    db.session.commit()
    print(f"Seeded {len(WORDS)} words successfully!")
