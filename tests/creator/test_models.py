import datetime

from django.test import TestCase
from freezegun import freeze_time

from creator.models import Subscription


class SubscriptionTestCase(TestCase):
    def setUp(self):
        pass
        # Subscription.objects.create(
        #
        # )

    def test_next_month(self):
        # Test some day before 28th for the same year and advancing one year
        with freeze_time("2018-04-07"):
            today = datetime.datetime.today()
            self.assertEqual(
                Subscription.next_month(today.day),
                today.replace(month=today.month+1)
            )

        with freeze_time("2018-12-07"):
            today = datetime.datetime.today()
            self.assertEqual(
                Subscription.next_month(today.day),
                today.replace(year=today.year+1, month=1)
            )

        # Test 29th day in february
        with freeze_time("2018-01-29"):
            today = datetime.datetime.today()
            self.assertEqual(
                Subscription.next_month(today.day),
                today.replace(month=2, day=28)
            )

        # Test 30th day in february
        with freeze_time("2018-01-30"):
            today = datetime.datetime.today()
            self.assertEqual(
                Subscription.next_month(today.day),
                today.replace(month=2, day=28)
            )

        # Test 31st day in february
        with freeze_time("2018-01-31"):
            today = datetime.datetime.today()
            self.assertEqual(
                Subscription.next_month(today.day),
                today.replace(month=2, day=28)
            )