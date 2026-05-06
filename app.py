import os
from flask import Flask
from models import db


app = Flask(__name__)

# Configure the SQLite database
# This creates a file named 'tracker.db' in the project folder
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tracker.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

# Import routes AFTER app is defined to avoid circular imports
from routes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates the database file and tables
    app.run(debug=False, port=8000)


@app.template_filter('format_seconds')
def format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"
