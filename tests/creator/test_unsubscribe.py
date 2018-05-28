import datetime
import re

import itsdangerous
from django.core import mail
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import TestCase, Client
from freezegun import freeze_time

from StundenzettelCreator import settings
from creator.models import Subscription

TEST_DATE = "2018-04-29"


class SubscribeClientTestCase(TestCase):
    # TODO: Implement
    pass


class UnsubscribeClientTestCase(TestCase):
    # TODO: Implement
    pass


class UnsubscribeTestCase(TestCase):
    @freeze_time(TEST_DATE)
    def setUp(self):
        self.subscription = Subscription.objects.create(
            email='test@test.com',
            first_name='test',
            surname='test',
            hours=5,
            unit_of_organisation='Test'
        )

        call_command('send_mails')

        self.client = Client()

        self.maxDiff = None

    def test_correct_unsubscribe_link(self):
        email = mail.outbox[0]

        # Checks that exactly one subscription is in the database and one email has been sent (setUp)
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

        # Verifies that the email contains an unsubscribe link and retrieves it
        match = re.search(r'({}/unsubscribe/)([\w.\-]+)[\n<]'.format(settings.HOST_NAME), email.body)
        self.assertTrue(match)

        # Retrieves token from the link
        unsubscribe_token = match.group(2)

        # Checks the signature of that link
        signer = itsdangerous.URLSafeTimedSerializer(settings.SECRET_KEY)
        with freeze_time(TEST_DATE):
            self.assertEqual(
                signer.loads(unsubscribe_token, max_age=60 * 60 * 24 * 7),
                self.subscription.pk
            )

        # The complete link
        unsubscribe_link = ''.join(match.group(1, 2))

        # Checks the view
        with freeze_time(TEST_DATE):
            response = self.client.get(unsubscribe_link)
        self.assertEqual(response.status_code, 200)
        self.assertHTMLEqual(
            response.content.decode(),
            render_to_string(
                template_name='creator/subscription_unsubscribe.html',
                context={'status': 'success'}
            )
        )

        # Checks that the subscription has indeed been deleted
        self.assertEqual(Subscription.objects.count(), 0)

    def test_tampered_unsubscribe_link(self):
        email = mail.outbox[0]

        # Checks that exactly one subscription is in the database and one email has been sent (setUp)
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

        # Verifies that the email contains an unsubscribe link and retrieves it
        match = re.search(r'({}/unsubscribe/)([\w.\-]+)[\n<]'.format(settings.HOST_NAME), email.body)
        self.assertTrue(match)

        # Gets the complete link and tampers with it
        unsubscribe_link = ''.join(match.group(1, 2))
        unsubscribe_link += 'something'

        # Checks the view
        with freeze_time(TEST_DATE):
            response = self.client.get(unsubscribe_link)
        self.assertEqual(response.status_code, 200)
        self.assertHTMLEqual(
            response.content.decode(),
            render_to_string(
                template_name='creator/subscription_unsubscribe.html',
                context={'status': 'failure', 'reason': 'tampered'}
            )
        )

        # Checks that it failed to unsubscribe
        self.assertEqual(Subscription.objects.count(), 1)

    def test_expired_unsubscribe_link(self):
        email = mail.outbox[0]

        # Checks that exactly one subscription is in the database
        self.assertEqual(Subscription.objects.count(), 1)

        # Verifies that the email contains an unsubscribe link and retrieves it
        match = re.search(r'({}/unsubscribe/)([\w.\-]+)[\n<]'.format(settings.HOST_NAME), email.body)
        self.assertTrue(match)

        # The complete link
        unsubscribe_link = ''.join(match.group(1, 2))

        # Checks the view
        next_week = datetime.datetime.strptime(TEST_DATE, '%Y-%m-%d') + datetime.timedelta(days=7, hours=1)
        with freeze_time(next_week):
            response = self.client.get(unsubscribe_link)
            self.assertEqual(response.status_code, 200)
            self.assertHTMLEqual(
                response.content.decode(),
                render_to_string(
                    template_name='creator/subscription_unsubscribe.html',
                    context={'status': 'failure', 'reason': 'expired'}
                )
            )

        # Checks that it failed to unsubscribe
        self.assertEqual(Subscription.objects.count(), 1)
