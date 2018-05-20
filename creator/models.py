import calendar
import datetime

from django.db import models
from easy_pdf.rendering import render_to_pdf

from creator.timesheet import generate_timesheet_data


class SubscriptionManager(models.Manager):
    def due_subscriptions(self):
        """Returns a QuerySet of all subscriptions if they are due

        If today is the next to last day of the current month, all subscriptions are returned. Else,
        an empty QuerySset will be returned.
        """
        today = datetime.datetime.today()
        last_day_of_month = calendar.monthrange(year=today.year, month=today.month)[1]

        # If today is the next to last day of the month
        if today.day == last_day_of_month - 1:
            # Return all the subscriptions
            return super(SubscriptionManager, self).get_queryset().all()
        else:
            # Else return an empty queryset
            return super(SubscriptionManager, self).none()


class Subscription(models.Model):
    email = models.EmailField()
    hours = models.IntegerField()
    unit_of_organisation = models.CharField(max_length=250)
    surname = models.CharField(max_length=300)
    first_name = models.CharField(max_length=200)

    objects = SubscriptionManager()

    def generate_pdf(self):
        today = datetime.datetime.today()
        data = {
            'surname': self.surname,
            'first_name': self.first_name,
            'year': today.year,
            'month': today.month,
            'hours': self.hours,
            'last_day_of_month': calendar.monthrange(today.year, today.month)[1],
            'unit_of_organisation': self.unit_of_organisation,
        }

        timesheet_data, header_date, total_hours = generate_timesheet_data(
            year=data['year'],
            month=data['month'],
            fdom=1,
            ldom=data['last_day_of_month'],
            hours=data['hours']
        )

        data.update({
            'timesheet_data': timesheet_data,
            'header_date': header_date,
            'total_hours': total_hours
        })

        return render_to_pdf(template='creator/timesheet.html', context=data)

    def __str__(self):
        return self.email
