import calendar
import datetime
import logging
import random

import itsdangerous
import numpy as np
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from easy_pdf.views import PDFTemplateView
import holidays

from creator.forms import DetailsForm, SubscriptionForm
from creator.models import Subscription

logger = logging.getLogger(__name__)


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
def generate_timesheet_data(details):
    """
    By Patrick Faion <https://github.com/pfaion/timesheet_generator>
    """
    year = details['year']
    month = details['month']
    fdom = details['first_day_of_month']
    ldom = details['last_day_of_month']

    # get public holidays and length of the month
    public_holidays = holidays.DE(state=details['state'], years=year)
    days_in_month = calendar.monthrange(year, month)[1]

    # check which days are valid, i.e. are specified workdays and not holidays
    valid_days = []
    for day in range(fdom, min(days_in_month, ldom) + 1):
        date = datetime.date(year, month, day)
        if date not in public_holidays and date.weekday() in details['days_of_week']:
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
    chunk_starts = np.arange(details['start_hour'], details['end_hour'], 0.5)

    # distribute all hours
    h = details['hours']
    while h > 0:
        if len(possible_days) == 0:
            raise RuntimeError("Could not work off all hours with given parameters!")
        # select day
        day, weight = weighted_choice(zip(possible_days, weights))
        # if day is already listed, extend working hours there either before or after
        if day in collector:
            start, end = collector[day]
            possible_extensions = []
            if start > details['start_hour']:
                possible_extensions.append('before')
            if end < (details['end_hour'] - 0.5):
                possible_extensions.append('after')
            extension = random.choice(possible_extensions)
            if extension == 'before':
                start -= 0.5
            if extension == 'after':
                end += 0.5
            collector[day] = (start, end)
            if end - start == details['max_hours']:
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
    total_hours_formatted = format_timedelta(datetime.timedelta(hours=details['hours']))

    return data, header_date, total_hours_formatted


class DetailsFormView(FormView):
    template_name = 'creator/home.html'
    form_class = DetailsForm
    success_url = '/result/'

    def form_valid(self, form):
        self.request.session['details'] = form.cleaned_data

        return super(DetailsFormView, self).form_valid(form)


class SubscriptionFormView(FormView):
    template_name = 'creator/subscription_subscribe.html'
    form_class = SubscriptionForm
    success_url = '/success/'

    def form_valid(self, form):
        subscription = Subscription.objects.create(
            email=form.cleaned_data['email'],
            first_send_date=form.cleaned_data['first_send_date'],
            next_send_date=form.cleaned_data['first_send_date'],
            hours=form.cleaned_data['hours'],
            unit_of_organisation=form.cleaned_data['unit_of_organisation'],
            first_name=form.cleaned_data['first_name'],
            surname=form.cleaned_data['surname']
        )

        self.request.session['subscription_id'] = subscription.pk

        return super().form_valid(form)


class SuccessView(DetailView):
    template_name = 'creator/subscription_success.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Subscription, pk=self.request.session['subscription_id']
        )


def unsubscribe(request, token):
    signer = itsdangerous.URLSafeTimedSerializer(secret_key=settings.SECRET_KEY)
    max_age = 60 * 60 * 24 * 7  # Seven days till the link expires

    try:
        subscription_id = signer.loads(token, max_age=max_age)
        # TODO: except no subscription found -> already unsubscribed?
        Subscription.objects.get(pk=subscription_id).delete()
        context = {
            'status': 'success',
        }
    except itsdangerous.SignatureExpired:
        context = {
            'status': 'failure',
            'reason': 'expired'
        }
        logger.warning('Unsubscribe link expired')
    except itsdangerous.BadTimeSignature as e:
        logger.error('Wrong signature format [{}]: {}'.format(e, token))
        context = {
            'status': 'failure',
            'reason': 'tampered'
        }
    except itsdangerous.BadSignature as e:
        context = {
            'status': 'failure',
            'reason': 'tampered'
        }
        logger.error('Tampering with unsubscribe link detected [{}]: {}'.format(e, token))

        encoded_payload = e.payload
        if encoded_payload is not None:
            try:
                decoded_payload = signer.load_payload(encoded_payload)
                logger.error('Payload was {}'.format(decoded_payload))
            except itsdangerous.BadData:
                pass

    return render(request, 'creator/subscription_unsubscribe.html', context=context)


class ResultPdfView(PDFTemplateView):
    template_name = 'creator/timesheet.html'

    def get_context_data(self, **kwargs):
        timesheet_data, header_date, total_hours = generate_timesheet_data(
            self.request.session.get('details'))

        return super(ResultPdfView, self).get_context_data(
            pagesize='A4',
            details=self.request.session.get('details'),
            data=timesheet_data,
            header_date=header_date,
            total_hours=total_hours
        )
