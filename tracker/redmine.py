import math
import os
from dotenv import load_dotenv
from redminelib import Redmine

from tracker.models import Activity

load_dotenv()

redmine_client = Redmine(
    os.environ["REDMINE_URL"],
    key=os.environ["REDMINE_API_KEY"],
)

def push_activity(activity: Activity):
    redmine_client.time_entry.create(
        issue_id = activity.issue_number,
        spent_on = activity.day.strftime("%Y-%m-%d"),
        hours = math.ceil(activity.total_duration_seconds / 60 / 60 / 4) * 4,
        comments = activity.note or "",
    )
