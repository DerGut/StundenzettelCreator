import datetime

from django.test import TestCase
from freezegun import freeze_time

from creator.models import Subscription

TEST_DATE1 = "2018-04-30"


class SubscriptionTestCase(TestCase):
    def setUp(self):
        with freeze_time("2018-04-15"):
            self.subscription_today = Subscription.objects.create(
                email='test@test.com',
                first_name='test',
                surname='test',
                hours=5,
                unit_of_organisation='Test'
            )

    def tearDown(self):
        Subscription.objects.all().delete()

    def test_due_subscriptions_at_end_of_month(self):
        with freeze_time("2018-04-29"):
            subscriptions = Subscription.objects.due_subscriptions()

        self.assertEqual(len(subscriptions), 1)
        self.assertEqual(subscriptions[0], self.subscription_today)

    def test_due_subscriptions_within_month(self):
        with freeze_time("2018-04-15"):
            subscriptions = Subscription.objects.due_subscriptions()

        self.assertEqual(len(subscriptions), 0)
