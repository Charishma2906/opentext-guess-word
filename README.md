# Guess the Word Game

A simple Python web-based game where players try to guess words. Built using **Flask** with HTML templates for the user interface.

---

## Features
- Player registration and login
- Daily word challenges
- Track guesses and scores
- Player dashboard with game history and reports
- Admin functionality to manage users and view reports

---

## Project Structure

opentext-guess-word/
│
├─ app.py # Main Flask application
├─ extensions.py # Flask extensions setup
├─ forms.py # WTForms for user input
├─ models.py # Database models
├─ seed_words.py # Initial word list for the game
├─ requirements.txt # Python dependencies
├─ test_db.py # Test database script
├─ utils.py # Utility functions
├─ templates/ # HTML templates for the UI
│ ├─ all_guesses.html
│ ├─ base.html
│ ├─ daily_report.html
│ ├─ game.jpg
│ ├─ index.html
│ ├─ login.html
│ ├─ pause.html
│ ├─ pause_popup.html
│ ├─ play.html
│ ├─ player_dashboard.html
│ ├─ player_home.html
│ ├─ register.html
│ ├─ user_report.html
│ └─ welcome.html
├─ .gitignore # Files/folders ignored by Git
└─ README.md # Project documentation

---

## How to Run

1. **Clone the repository:**
```bash
git clone https://github.com/Charishma2906/opentext-guess-word.git
cd opentext-guess-word
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the Flask app:
```bash
python app.py
```

4. Open your browser and go to:
 http://127.0.0.1:5000

5. Start playing the game!
- Register as a player
- Try daily word challenges
- Track your scores and reports

## Notes
- The database file (__instance/guessword.db__) is local only. It will be created automatically when you run the app.
- Make sure Flask and the packages in __requirements.txt__ are installed.
- Do not modify the database manually unless needed for testing.

## Author
**Vemasani Charishma Chowdary**

## Contact
Email: vcharishmachowdary@gmail.com

