import calendar
import datetime

from django.core.management.base import BaseCommand, CommandError

from creator.models import Subscription


class Command(BaseCommand):
    help = 'Looks up all mail subscriptions in the DB, generates the corresponding PDF and sends off an email'

    def __init__(self):
        super().__init__()

        # Set current datetime and get length of next month
        self.today = datetime.datetime.today()
        if self.today.month == 12:
            self.last_day_of_next_month = calendar.monthrange(year=self.today.year+1, month=1)[1]
        else:
            self.last_day_of_next_month = calendar.monthrange(year=self.today.year, month=self.today.month+1)[1]

    def handle(self, *args, **options):
        subscriptions = Subscription.objects.filter(next_send_date__exact=self.today)

        for subscription in subscriptions:
            # Generate the pdf for the subscriber and send it off
            pdf = self.generate_pdf(subscription)
            self.send_email(subscription, pdf)

            # TODO: Improve this somehow such that each subscription won't need its own database access
            # Update the subscription to have a mail sent next month again
            Subscription.objects.get(pk=subscription.pk).update(self.next_month(subscription))

    def send_email(self, subscription, pdf):
        # Send email with pdf as attachment
        pass

    def generate_pdf(self, subscription):
        # TODO: Make the pdf generation independent of a view and save it as file (or object)
        pass

    def next_month(self, subscription):
        """Computes the same day as first_send_date of the next month or the last day of month if it is shorter"""

        # Decide whether to use the same day as first_send_date next month or the last_day_of_next_month
        if subscription.first_send_date.day <= self.last_day_of_next_month:
            day = subscription.first_send_date.day
        else:
            day = self.last_day_of_next_month

        # Get the next month + year
        if self.today.month == 12:
            year = self.today.year + 1
            month = 1
        else:
            year = self.today.year
            month = self.today.month + 1

        return datetime.datetime(year=year, month=month, day=day)
