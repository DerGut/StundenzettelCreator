import logging

import itsdangerous
import requests
from django.core import mail
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from StundenzettelCreator import settings

from creator.exceptions import TimesheetCreationError
from creator.models import Subscription

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Looks up all mail subscriptions in the DB, generates the corresponding PDF and sends off an email'

    def __init__(self):
        super().__init__()

        self.signer = itsdangerous.URLSafeTimedSerializer(secret_key=settings.SECRET_KEY)

    def handle(self, *args, **options):
        # Get subscriptions which next send date is today
        subscriptions = Subscription.objects.due_subscriptions()
        if not subscriptions:
            logger.info("No email subscriptions for today")
            return

        logger.info("Starting to send due email subscriptions")

        emails = []
        for subscription in subscriptions:
            # Generate the pdf for the subscriber and send it off
            try:
                pdf = subscription.generate_pdf()
                emails.append(self.new_email(subscription, pdf))
            except TimesheetCreationError:
                # TODO: Send an email-notification/ warning #29
                pass

        # Send off the actual mails
        connection = mail.get_connection()
        mails_sent = connection.send_messages(emails)
        connection.close()

        snitch_data = {'m': ''}

        # Logging
        num_subscriptions = subscriptions.count()
        if num_subscriptions > 0:
            msg = 'Sent off {} mails successfully'.format(mails_sent)
            logger.info(msg)
            snitch_data['m'] += msg
            if num_subscriptions - mails_sent > 0:
                msg = 'Failed to send {} mails'.format(num_subscriptions - mails_sent)
                logger.error(msg)
                snitch_data['m'] += (msg)
        else:
            msg = 'No subscriptions found'
            logger.info(msg)
            snitch_data += msg

        # Dead mans snitch
        if settings.SNITCH_URL:
            requests.post(settings.SNITCH_URL, data=snitch_data)

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
