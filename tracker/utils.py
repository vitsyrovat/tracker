from datetime import date,timedelta

import calendar


def add_months(base_date, months):
    month_index = (base_date.month - 1) + months
    year = base_date.year + (month_index // 12)
    month = (month_index % 12) + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(base_date.day, last_day)
    return base_date.replace(year=year, month=month, day=day)


def format_date_span(start_date, end_date):
    if start_date.year == end_date.year:
        if start_date.month == end_date.month:
            return f'{start_date.strftime("%b")} {start_date.day}–{end_date.day}, {start_date.year}'
        return f'{start_date.strftime("%b")} {start_date.day} – {end_date.strftime("%b")} {end_date.day}, {start_date.year}'
    return f'{start_date.strftime("%b")} {start_date.day}, {start_date.year} – {end_date.strftime("%b")} {end_date.day}, {end_date.year}'


def get_date_range(view_type, offset):
    today = date.today()
    if view_type == 'month':
        target_date = add_months(today.replace(day=1), offset)
        start_date = target_date.replace(day=1)
        last_day = calendar.monthrange(start_date.year, start_date.month)[1]
        end_date = start_date.replace(day=last_day)
    else:  # Default to week
        start_date = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
        end_date = start_date + timedelta(days=6)
    return start_date, end_date
