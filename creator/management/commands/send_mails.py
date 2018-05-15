import logging

import itsdangerous
from django.core import mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from easy_pdf.rendering import render_to_pdf

from StundenzettelCreator import settings

from creator.exceptions import TimesheetCreationError
from creator.models import Subscription
from creator.timesheet import generate_timesheet_data

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Looks up all mail subscriptions in the DB, generates the corresponding PDF and sends off an email'

    def __init__(self):
        super().__init__()

        self.signer = itsdangerous.URLSafeTimedSerializer(secret_key=settings.SECRET_KEY)

    def handle(self, *args, **options):
        logger.info("Starting to send todays email subscriptions")

        # Get subscriptions which next send date is today
        subscriptions = Subscription.objects.todays()

        emails = []
        for subscription in subscriptions:
            # Generate the pdf for the subscriber and send it off
            try:
                pdf = self.generate_pdf(subscription)
                emails.append(self.new_email(subscription, pdf))

                # TODO: Improve this somehow such that each subscription won't need its own database access
                # Update the subscription to have a mail sent next month again
                subscription.update_to_next_month()
            except TimesheetCreationError:
                # Delays the email to tomorrow
                pass

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

    def new_email(self, subscription, pdf):
        """Send email with pdf as attachment"""
        subject = "StundenzettelCreator - Your monthly timesheet"

        unsubscribe_hash = self.signer.dumps(subscription.pk)
        logger.debug('Created hash {}'.format(unsubscribe_hash))

        text_content = """
        Hey {first_name},
        
        here is your monthly timesheet from StundenzettelCreator.
        
        You can always unsubscribe with this link: {host}/unsubscribe/{token}
        
        Bye 
        """.format(
            first_name=subscription.first_name,
            host=settings.HOST_NAME,
            token=unsubscribe_hash,
        )

        html_content = render_to_string(
            'creator/subscription_email.html',
            context={
                'subscription': subscription,
                'host': settings.HOST_NAME,
                'token': unsubscribe_hash,
            })

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
        data = {
            'surname': subscription.surname,
            'first_name': subscription.first_name,
            'year': subscription.next_send_date.year,
            'month': subscription.next_send_date.month,
            'hours': subscription.hours,
            'last_day_of_month': subscription.next_send_date.day - 1,
            'unit_of_organisation': subscription.unit_of_organisation,
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
