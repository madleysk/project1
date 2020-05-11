. venv/bin/activate
export DATABASE_URL='sqlite:///mydb.sqlite3'
export SECRET_KEY=b'_9#y6K"G4Q0c\n\xec]/'
export FLASK_APP=application.py
export FLASK_ENV=development
flask run
