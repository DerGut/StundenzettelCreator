import calendar
import datetime
import logging

from django.core import mail
from django.core.management.base import BaseCommand, CommandError
from easy_pdf.rendering import render_to_pdf

from creator import forms
from creator.models import Subscription
from creator.views import generate_timesheet_data

logger = logging.getLogger(__name__)


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
        logger.info("Starting to send todays email subscriptions")
        subscriptions = Subscription.objects.filter(next_send_date__exact=self.today)

        emails = []
        for subscription in subscriptions:
            # Generate the pdf for the subscriber and send it off
            pdf = self.generate_pdf(subscription)
            emails.append(self.new_email(subscription, pdf))

            # TODO: Improve this somehow such that each subscription won't need its own database access
            # Update the subscription to have a mail sent next month again
            Subscription.objects.get(pk=subscription.pk).update(self.next_month(subscription))

        # Send off the actual mails
        connection = mail.get_connection()
        mails_sent = connection.send_messages(emails)
        connection.close()

        # Logging
        num_subscriptions = subscriptions.count()
        if num_subscriptions > 0:
            logger.info('Sent off {} mails successfully'.format(mails_sent))
            logger.error('Failed to send {} mails'.format(subscriptions.count()))
        else:
            logger.info('No subscriptions found')

    def new_email(self, subscription, pdf):
        """Send email with pdf as attachment"""

        subject = "StundenzettelCreator - Your monthly timesheet"
        message = """
        Hey {first_name},
        
        
        """.format(first_name=subscription.first_name)
        from_email = ""
        recipient_list = [subscription.email]

        email = mail.EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
            attachments=[('filename', pdf, 'application/pdf')],

        )

        return email

    def generate_pdf(self, subscription):
        details = forms.defaults
        details.update({
            'name': subscription.name,
            'first_name': subscription.first_name,
            'year': self.today.year,
            'month': self.today.month,
            'hours': subscription.hours,
            'unit_of_organisation': subscription.unit_of_organisation,
        })

        timesheet_data, header_date, total_hours = generate_timesheet_data(details)

        context = {
            'details': details,
            'data': timesheet_data,
            'header_date': header_date,
            'total_hours': total_hours
        }

        return render_to_pdf(template='creator/timesheet.html', context=context)

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

