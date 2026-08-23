from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()


class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), nullable=False, default='')
    day = db.Column(db.Date, nullable=False, default=date.today)

    duration_seconds = db.Column(db.Integer, default=0)
    note = db.Column(db.Text)

    # Timer state (used to calculate elapsed time when 'stop' is pressed)
    last_start_time = db.Column(db.DateTime, nullable=True)
    is_running = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Activity {self.name} on {self.day}>'

    @property
    def total_duration_seconds(self) -> int:
        if self.is_running and self.last_start_time is not None:
            return self.duration_seconds + (datetime.now() - self.last_start_time).seconds
        else:
            return self.duration_seconds

    # @property
    # def display(self) -> str:
    #     return f'{self.id}: {self.name} on {self.day}'
    #
    # def get_redmine_payload(self):
    #     # Convert duration_seconds to hours and minutes
    #     total_seconds = self.total_duration_seconds
    #     hours = total_seconds // 3600
    #     minutes = (total_seconds % 3600) // 60
    #
    #     payload = {
    #         'issue_id': 123,  # Replace with actual issue ID
    #         'spent_on': self.day.isoformat(),
    #         'hours': hours,
    #         'minutes': minutes,
    #         'comments': self.note or ''
    #     }
    #     return payload