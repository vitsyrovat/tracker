from datetime import datetime
from flask import Blueprint, request, redirect, url_for, jsonify
from sqlalchemy.exc import IntegrityError

from tracker.models import db, Activity
from tracker.serialization import serialize_activity, parse_activity_label

bp = Blueprint('activities', __name__, url_prefix='/activities')

@bp.route('/', methods=['POST'])
def create_activity():
    payload = request.get_json(silent=True) or {}
    day_str = payload.get('day', '')

    if not day_str:
        return jsonify({'ok': False, 'error': 'Day is required.'}), 400
    try:
        day_obj = datetime.strptime(day_str, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'Invalid day value.'}), 400

    label_stripped = (payload.get('label') or '').strip()
    if not label_stripped:
        return jsonify({'ok': False, 'error': 'Enter activity label.'}), 400

    duration_str = payload.get('duration_seconds', '0')
    try:
        duration_int = int(duration_str)
    except (TypeError, ValueError):
        return jsonify({'ok': False, 'error': 'Invalid duration value.'}), 400
    if duration_int < 0:
        return jsonify({'ok': False, 'error': 'Duration must be zero or positive.'}), 400

    issue_number, name, comment = parse_activity_label(label_stripped)

    activity = Activity(
        issue_number=issue_number,
        name=name or '',
        note=comment or '',
        day=day_obj,
        duration_seconds=duration_int,
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


@bp.route('/<int:id>', methods=['PATCH'])
def update_activity(id):
    activity = Activity.query.get_or_404(id)
    payload = request.get_json(silent=True) or {}
    field = payload.get('field')
    value = payload.get('value')

    if field == 'label':
        cleaned_name = (value or '').strip()
        if not cleaned_name:
            return jsonify({'ok': False, 'error': 'Name cannot be empty.'}), 400

        issue_number, name, note = parse_activity_label(cleaned_name)

        activity.name = name
        activity.note = note
        activity.issue_number = issue_number

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


@bp.route('/<int:id>/start', methods=['POST'])
def start_activity(id):
    activity = Activity.query.get_or_404(id)
    if not activity.is_running:
        activity.is_running = True
        activity.last_start_time = datetime.now()
        db.session.commit()

    return redirect(request.referrer or url_for('main.dashboard'))


@bp.route('/<int:id>/stop', methods=['POST'])
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

    return redirect(request.referrer or url_for('main.ashboard'))


@bp.route('/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.get_or_404(id)
    db.session.delete(activity)
    db.session.commit()
    return jsonify({'ok': True}), 200


@bp.route('/<int:id>/push-to-redmine', methods=['POST'])
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

