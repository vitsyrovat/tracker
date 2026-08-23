from flask import render_template, request, redirect, url_for, jsonify
from sqlalchemy.exc import IntegrityError

from tracker.app import app
from tracker.models import db, Activity
from datetime import date, datetime, timedelta

from tracker.utils import format_date_span, get_date_range


def serialize_activity(activity):
    return {
        'id': activity.id,
        'name': activity.name,
        'duration_seconds': activity.duration_seconds,
        'total_duration_seconds': activity.total_duration_seconds,
        'is_running': activity.is_running,
        'day': activity.day.isoformat(),
    }


@app.route('/')
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



@app.route('/activity', methods=['POST'])
def create_activity():
    payload = request.get_json(silent=True) or {}
    day_str = payload.get('day')

    if not day_str:
        return jsonify({'ok': False, 'error': 'Day is required.'}), 400

    try:
        day_obj = datetime.strptime(day_str, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'Invalid day value.'}), 400

    cleaned_name = (payload.get('name') or '').strip()
    if len(cleaned_name) > 100:
        return jsonify({'ok': False, 'error': 'Name is too long.'}), 400

    duration_value = payload.get('duration_seconds')
    if duration_value in (None, ''):
        duration_seconds = 0
    else:
        try:
            duration_seconds = int(duration_value)
        except (TypeError, ValueError):
            return jsonify({'ok': False, 'error': 'Invalid duration value.'}), 400

    if duration_seconds < 0:
        return jsonify({'ok': False, 'error': 'Duration must be zero or positive.'}), 400

    if not cleaned_name and duration_value in (None, ''):
        return jsonify({'ok': False, 'error': 'Enter a name or a duration.'}), 400

    activity = Activity(
        name=cleaned_name or '',
        day=day_obj,
        duration_seconds=duration_seconds,
        is_running=False,
        last_start_time=None,
    )

    try:
        db.session.add(activity)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'ok': False, 'error': 'Could not create activity.'}), 500

    return jsonify({'ok': True, 'activity': serialize_activity(activity)}), 201


@app.route('/activity/<int:id>'
           '', methods=['PATCH'])
def update_activity(id):
    activity = Activity.query.get_or_404(id)
    payload = request.get_json(silent=True) or {}
    field = payload.get('field')
    value = payload.get('value')

    if field == 'name':
        cleaned_name = (value or '').strip()
        if not cleaned_name:
            return jsonify({'ok': False, 'error': 'Name cannot be empty.'}), 400
        if len(cleaned_name) > 100:
            return jsonify({'ok': False, 'error': 'Name is too long.'}), 400
        activity.name = cleaned_name
    elif field == 'duration_seconds':
        try:
            duration_seconds = int(value)
        except (TypeError, ValueError):
            return jsonify({'ok': False, 'error': 'Invalid duration value.'}), 400

        if duration_seconds < 0:
            return jsonify({'ok': False, 'error': 'Duration must be zero or positive.'}), 400
        activity.duration_seconds = duration_seconds
    else:
        return jsonify({'ok': False, 'error': 'Unsupported field.'}), 400

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'ok': False, 'error': 'Could not save activity.'}), 500

    return jsonify({'ok': True, 'activity': serialize_activity(activity)})


@app.route('/activity/<int:id>/start', methods=['POST'])
def start_activity(id):
    activity = Activity.query.get_or_404(id)
    if not activity.is_running:
        activity.is_running = True
        activity.last_start_time = datetime.now()
        db.session.commit()

    return redirect(request.referrer or url_for('dashboard'))


@app.route('/activity/<int:id>/stop', methods=['POST'])
def stop_activity(id):
    activity = Activity.query.get_or_404(id)
    if activity.is_running and activity.last_start_time:
        # Calculate difference between NOW and the saved START time
        now = datetime.now()
        elapsed = now - activity.last_start_time

        # Add the elapsed seconds to the existing total
        activity.duration_seconds += int(elapsed.total_seconds())

        # Reset state
        activity.is_running = False
        activity.last_start_time = None
        db.session.commit()

    return redirect(request.referrer or url_for('dashboard'))


@app.route('/activity/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get_or_404(id)
    db.session.delete(activity)
    db.session.commit()
    return jsonify({'ok': True}), 200


@app.route('/activity/<int:id>/push-to-redmine', methods=['POST'])
def push_activity(id):
    activity = Activity.query.get_or_404(id)
    # db.session.delete(activity)
    # db.session.commit()

    # redmine_client.time_entry.create(
    #     issue_id=task_id,
    #     spent_on=result_date,
    #     hours=hours,
    #     comments=desc_text,
    return jsonify({'ok': True}), 200

