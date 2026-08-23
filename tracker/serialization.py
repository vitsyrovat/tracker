import re


def serialize_activity(activity):
    return {
        'id': activity.id,
        'name': activity.name,
        'label': activity.label,
        'duration_seconds': activity.duration_seconds,
        'total_duration_seconds': activity.total_duration_seconds,
        'is_running': activity.is_running,
        'day': activity.day.isoformat(),
    }


def parse_activity_label(label: str) -> tuple[int | None, str | None, str | None]:
    number = None
    comment = None

    # Number: #123
    match = re.search(r'#(\d+)', label)
    if match:
        number = int(match.group(1))
        label = label[match.end():]

    # Comment: everything inside the outermost parentheses
    match = re.search(r'\((.*)\)\s*$', label)
    if match:
        comment = match.group(1).strip()
        before_comment = label[:match.start()]
    else:
        before_comment = label

    # Name: everything between issue number and comment
    name = before_comment.strip(' -')

    return number, name, comment
