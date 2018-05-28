from django.test import TestCase
from freezegun import freeze_time

from creator.exceptions import TimesheetCreationError
from creator.models import Subscription


class SubscriptionManagerTestCase(TestCase):
    def setUp(self):
        with freeze_time("2018-04-15"):
            self.subscription_today = Subscription.objects.create(
                email='test@test.com',
                first_name='test',
                surname='test',
                hours=5,
                unit_of_organisation='Test'
            )

    def test_due_subscriptions_at_end_of_month(self):
        with freeze_time("2018-04-29"):
            subscriptions = Subscription.objects.due_subscriptions()

        self.assertEqual(len(subscriptions), 1)
        self.assertEqual(subscriptions[0], self.subscription_today)

    def test_due_subscriptions_within_month(self):
        with freeze_time("2018-04-15"):
            subscriptions = Subscription.objects.due_subscriptions()

        self.assertEqual(len(subscriptions), 0)


class SubscriptionTestCase(TestCase):
    def test_generate_pdf_with_valid_data(self):
        with freeze_time("2018-04-15"):
            subscription = Subscription.objects.create(
                email='test@test.com',
                first_name='test',
                surname='test',
                hours=5,
                unit_of_organisation='Test'
            )
        pdf = subscription.generate_pdf()
        self.assertIsInstance(pdf, bytes)

    def test_generate_pdf_with_invalid_data(self):
        with freeze_time("2018-04-15"):
            subscription = Subscription.objects.create(
                email='test@test.com',
                first_name='test',
                surname='test',
                hours=500,
                unit_of_organisation='Test'
            )
        self.assertRaisesMessage(
            TimesheetCreationError,
            "Too many hours for specified range of month",
            subscription.generate_pdf
        )
