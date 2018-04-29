import calendar
import datetime

from django.db import models


class SubscriptionManager(models.Manager):
    def todays(self):
        """Returns a QuerySet of all subscriptions which next send date is due today

        Note, this method also returns all subscriptions which next send date has been in the past.
        This prevents subscriptions from being skipped in case the scheduler fails to execute
        the send_mail command on a specific day. Returning all subscription <= today, skipped
        subscriptions would simply be processed on the following day.
        """
        return super().get_queryset().filter(next_send_date__lte=datetime.datetime.today())


class Subscription(models.Model):
    email = models.EmailField()
    first_send_date = models.DateField()
    next_send_date = models.DateField()
    hours = models.IntegerField()
    unit_of_organisation = models.CharField(max_length=250)
    name = models.CharField(max_length=300)
    first_name = models.CharField(max_length=200)

    objects = SubscriptionManager()

    def update_to_next_month(self):
        self.next_send_date = self.next_month(self.first_send_date.day)
        self.save()

    @classmethod
    def next_month(cls, original_day):
        """Computes the same day as first_send_date of the next month or the last day of month if it is shorter"""
        today = datetime.datetime.today()
        if today.month == 12:
            last_day_of_next_month = calendar.monthrange(year=today.year+1, month=1)[1]
        else:
            last_day_of_next_month = calendar.monthrange(year=today.year, month=today.month+1)[1]

        # Decide whether to use the same day as first_send_date next month or the last_day_of_next_month
        if original_day <= last_day_of_next_month:
            day = original_day
        else:
            day = last_day_of_next_month

        # Get the next month + year
        if today.month == 12:
            year = today.year + 1
            month = 1
        else:
            year = today.year
            month = today.month + 1

        return datetime.datetime(year=year, month=month, day=day)

    def __str__(self):
        return '{} - day {}'.format(self.email, self.next_send_date)