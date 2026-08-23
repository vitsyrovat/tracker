from flask import Blueprint, render_template, request
from datetime import date, timedelta

from tracker.models import Activity
from tracker.utils import format_date_span, get_date_range

bp = Blueprint('main', __name__)


@bp.route("/")
def dashboard():
    view = request.args.get('view', 'week')
    offset = int(request.args.get('offset', 0))
    start_date, end_date = get_date_range(view, offset)
    heading_label = (
        start_date.strftime('%B %Y')
        if view == 'month'
        else format_date_span(start_date, end_date)
    )

    # 1. Fetch activities from DB
    activities_db = Activity.query.filter(
        Activity.day >= start_date,
        Activity.day <= end_date
    ).all()

    # 2. Organize activities by date
    # Result structure: { date(2023,10,27): [Activity1, Activity2], ... }
    activities_by_day = {}
    total_seconds_by_day = {}
    for act in activities_db:
        if act.day not in activities_by_day:
            activities_by_day[act.day] = []
            total_seconds_by_day[act.day] = 0
        activities_by_day[act.day].append(act)
        total_seconds_by_day[act.day] += act.total_duration_seconds

    # 3. Create a sorted list of all dates in the range
    all_days = []
    curr = start_date
    while curr <= end_date:
        all_days.append(curr)
        # Initialize zero total for days with no activities
        if curr not in total_seconds_by_day:
            total_seconds_by_day[curr] = 0
        curr += timedelta(days=1)


    return render_template('dashboard.html',
                           all_days=all_days,
                           activities_by_day=activities_by_day,
                           total_seconds_by_day=total_seconds_by_day,
                           view=view,
                           offset=offset,
                           start_date=start_date,
                           end_date=end_date,
                           heading_label=heading_label,
                           date=date)  # Pass the date class for comparisons
