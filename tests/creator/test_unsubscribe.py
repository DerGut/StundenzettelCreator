import datetime
import re

import itsdangerous
from django.core import mail
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import TestCase, Client

from StundenzettelCreator import settings
from creator.models import Subscription


class UnsubscribeTestCase(TestCase):
    def setUp(self):
        today = datetime.datetime.today()
        self.subscription = Subscription.objects.create(
            email='test@test.com',
            first_name='test',
            surname='test',
            first_send_date=today,
            next_send_date=today,
            hours=10,
            unit_of_organisation='Test'
        )

        call_command('send_mails')

    def test_unsubscribe(self):
        email = mail.outbox[0]
        match = re.search(r'{}/unsubscribe/([\w.\-]+)[\n<]'.format(settings.HOST_NAME), email.body)
        self.assertTrue(match)

        # Retrieves the match inside the parantheses
        unsubscribe_token = match.group(1)

        signer = itsdangerous.URLSafeTimedSerializer(settings.SECRET_KEY)
        self.assertEqual(
            signer.loads(unsubscribe_token, max_age=60*60*24*7),
            self.subscription.pk
        )

        client = Client()
        response = client.get(match.group(0))
        self.assertEqual(response.status_code, 200)

        self.assertHTMLEqual(
            response.content.decode(),
            render_to_string(
                template_name='creator/subscription_unsubscribe.html',
                context={'status': 'success'}
            )
        )
