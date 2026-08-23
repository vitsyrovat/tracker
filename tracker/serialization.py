def serialize_activity(activity):
    return {
        'id': activity.id,
        'name': activity.name,
        'duration_seconds': activity.duration_seconds,
        'total_duration_seconds': activity.total_duration_seconds,
        'is_running': activity.is_running,
        'day': activity.day.isoformat(),
    }
