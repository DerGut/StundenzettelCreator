import datetime

from django.test import TestCase
from freezegun import freeze_time

from creator.models import Subscription

TEST_DATE1 = "2018-04-30"


class SubscriptionTestCase(TestCase):

    def tearDown(self):
        Subscription.objects.all().delete()

    def test_todays_queryset(self):
        with freeze_time("2018-04-30"):
            today = datetime.datetime.today()
            self.subscription_today = Subscription.objects.create(
                email='test@test.com',
                first_name='test',
                surname='test',
                first_send_date=today,
                next_send_date=today,
                hours=5,
                unit_of_organisation='Test'
            )
            todays = Subscription.objects.todays()

        self.assertEqual(len(todays), 1)
        self.assertEqual(todays[0], self.subscription_today)

    def test_next_month(self):
        # Test some day before 28th for the same year and advancing one year
        with freeze_time("2018-04-07"):
            today = datetime.datetime.today()
            subscription = Subscription.objects.create(
                email='test@test.com',
                first_name='test',
                surname='test',
                first_send_date=today,
                next_send_date=today,
                hours=5,
                unit_of_organisation='Test'
            )
            self.assertEqual(
                subscription.next_month(today.day),
                today.replace(month=today.month+1)
            )

        with freeze_time("2018-12-07"):
            today = datetime.datetime.today()
            subscription = Subscription.objects.create(
                email='test@test.com',
                first_name='test',
                surname='test',
                first_send_date=today,
                next_send_date=today,
                hours=5,
                unit_of_organisation='Test'
            )
            self.assertEqual(
                subscription.next_month(today.day),
                today.replace(year=today.year+1, month=1)
            )

        # Test 29th day in february
        with freeze_time("2018-01-29"):
            today = datetime.datetime.today()
            subscription = Subscription.objects.create(
                email='test@test.com',
                first_name='test',
                surname='test',
                first_send_date=today,
                next_send_date=today,
                hours=5,
                unit_of_organisation='Test'
            )
            self.assertEqual(
                subscription.next_month(today.day),
                today.replace(month=2, day=28)
            )

        # Test 30th day in february
        with freeze_time("2018-01-30"):
            today = datetime.datetime.today()
            subscription = Subscription.objects.create(
                email='test@test.com',
                first_name='test',
                surname='test',
                first_send_date=today,
                next_send_date=today,
                hours=5,
                unit_of_organisation='Test'
            )
            self.assertEqual(
                subscription.next_month(today.day),
                today.replace(month=2, day=28)
            )

        # Test 31st day in february
        with freeze_time("2018-01-31"):
            today = datetime.datetime.today()
            subscription = Subscription.objects.create(
                email='test@test.com',
                first_name='test',
                surname='test',
                first_send_date=today,
                next_send_date=today,
                hours=5,
                unit_of_organisation='Test'
            )
            self.assertEqual(
                subscription.next_month(today.day),
                today.replace(month=2, day=28)
            )
