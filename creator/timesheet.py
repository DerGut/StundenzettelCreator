"""
   Based on the original script timesheet.py by Patrick Faion
   https://github.com/pfaion/timesheet_generator

    :license: The Unlicense
"""

import calendar
import datetime
import random

import holidays
import numpy as np

from creator.exceptions import TimesheetCreationError


def format_timedelta(td):
    """Format datetime.timedelta as "hh:mm"."""
    s = td.total_seconds()
    return "{:0>2d}:{:0>2d}".format(int(s // 3600), int((s % 3600) // 60))


def weighted_choice(choices):
    """Select random choice from list of (option, weight) pairs according to the weights."""
    choices = list(choices)
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c, w
        upto += w
    return c, w


# TODO: Take this logic out of views.py
def generate_timesheet_data(year, month, fdom, ldom, hours):
    """
    By Patrick Faion <https://github.com/pfaion/timesheet_generator>
    """
    days_of_week = [0, 1, 2, 3, 4]
    start_hour = 8
    end_hour = 18
    max_hours = 6
    state = 'NI'

    # get public holidays and length of the month
    public_holidays = holidays.DE(state=state, years=year)
    days_in_month = calendar.monthrange(year, month)[1]

    # check which days are valid, i.e. are specified workdays and not holidays
    valid_days = []
    for day in range(fdom, min(days_in_month, ldom) + 1):
        date = datetime.date(year, month, day)
        if date not in public_holidays and date.weekday() in days_of_week:
            valid_days.append(day)

    # Distribute hours over valid days. Use exponential weights (after random shuffle) for days,
    # so some days are used often and some are used rarely.
    possible_days = valid_days
    random.shuffle(possible_days)
    weights = list(1 / np.arange(1, len(possible_days) + 1))

    # collector for sampled distribution
    # day => (start, end)
    collector = dict()

    # possible chunks over the day are from start to end in steps of half-hours
    chunk_starts = np.arange(start_hour, end_hour, 0.5)

    # distribute all hours
    h = hours
    while h > 0:
        if len(possible_days) == 0:
            raise TimesheetCreationError("Too many hours for specified range of month")
        # select day
        day, weight = weighted_choice(zip(possible_days, weights))
        # if day is already listed, extend working hours there either before or after
        if day in collector:
            start, end = collector[day]
            possible_extensions = []
            if start > start_hour:
                possible_extensions.append('before')
            if end < (end_hour - 0.5):
                possible_extensions.append('after')
            extension = random.choice(possible_extensions)
            if extension == 'before':
                start -= 0.5
            if extension == 'after':
                end += 0.5
            collector[day] = (start, end)
            if end - start == max_hours:
                possible_days.remove(day)
                weights.remove(weight)
        # if day not yet listed, select random starting chunk
        else:
            start = random.choice(chunk_starts)
            end = start + 0.5
            collector[day] = (start, end)
        # half and hour was distributed off
        h -= 0.5

    data = []
    for day in range(1, days_in_month + 1):
        if day in collector:
            date = datetime.date(year, month, day)
            s, e = collector[day]
            s_h = int(s)
            s_m = int((s % 1) * 60)
            e_h = int(e)
            e_m = int((e % 1) * 60)
            start = datetime.datetime.combine(date, datetime.time(s_h, s_m))
            end = datetime.datetime.combine(date, datetime.time(e_h, e_m))
            duration = end - start
            data.append({
                'day': "{}.".format(day),
                'start': start.strftime("%H:%M"),
                'end': end.strftime("%H:%M"),
                'duration': format_timedelta(duration),
                'date': date.strftime("%d.%m.")
            })
        else:
            data.append({
                'day': "{}.".format(day),
                'start': "",
                'end': "",
                'duration': "",
                'date': ""
            })

    # additional format strings
    header_date = "{:0>2d}/{}".format(month, year)
    total_hours_formatted = format_timedelta(datetime.timedelta(hours=hours))

    return data, header_date, total_hours_formatted
