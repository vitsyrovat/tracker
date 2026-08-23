from pathlib import Path
from flask import Flask
from tracker.models import db
from tracker.routes.activities import bp as activities_bp
from tracker.routes.main import bp as main_bp


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)

app.register_blueprint(main_bp)
app.register_blueprint(activities_bp)


# Configure the SQLite database
# This creates a file named 'tracker.db' in the project folder
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR.parent / 'tracker.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

@app.template_filter('format_seconds')
def format_seconds(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m"


# Import routes AFTER app is defined to avoid circular imports
# from tracker import routes  # noqa: E402, F401
