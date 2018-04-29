import logging

from django.core import mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from easy_pdf.rendering import render_to_pdf

from creator import forms
from creator.models import Subscription
from creator.views import generate_timesheet_data

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Looks up all mail subscriptions in the DB, generates the corresponding PDF and sends off an email'

    def handle(self, *args, **options):
        logger.info("Starting to send todays email subscriptions")

        # Get subscriptions which next send date is today
        subscriptions = Subscription.objects.todays()

        emails = []
        for subscription in subscriptions:
            # Generate the pdf for the subscriber and send it off
            pdf = self.generate_pdf(subscription)
            emails.append(self.new_email(subscription, pdf))

            # TODO: Improve this somehow such that each subscription won't need its own database access
            # Update the subscription to have a mail sent next month again
            subscription.update_to_next_month()

        # Send off the actual mails
        connection = mail.get_connection()
        mails_sent = connection.send_messages(emails)
        connection.close()

        # Logging
        num_subscriptions = subscriptions.count()
        if num_subscriptions > 0:
            logger.info('Sent off {} mails successfully'.format(mails_sent))
            if num_subscriptions - mails_sent > 0:
                logger.error('Failed to send {} mails'.format(num_subscriptions - mails_sent))
        else:
            logger.info('No subscriptions found')

    @classmethod
    def new_email(cls, subscription, pdf):
        """Send email with pdf as attachment"""

        subject = "StundenzettelCreator - Your monthly timesheet"

        text_content = """
        Hey {first_name},
        
        here is your monthly timesheet from StundenzettelCreator.
        
        Bye 
        """.format(first_name=subscription.first_name)
        html_content = render_to_string('creator/email_subscription.html', {'context': subscription})

        from_email = "subscription@stundenzettel-creator.xyz"
        recipient_list = [subscription.email]

        email = mail.EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list,
            attachments=[('filename', pdf, 'application/pdf')],
        )
        email.attach_alternative(html_content, 'text/html')

        return email

    @classmethod
    def generate_pdf(cls, subscription):
        details = forms.defaults
        details.update({
            'name': subscription.name,
            'first_name': subscription.first_name,
            'year': subscription.next_send_date.year,
            'month': subscription.next_send_date.month,
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
