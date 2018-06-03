import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from creator.fields import DateRangeField


class DateRangeFieldTestCase(TestCase):
    def setUp(self):
        self.field = DateRangeField()

    def test_valid_input(self):
        date_tuple = (
            datetime.date(year=2018, month=5, day=1),
            datetime.date(year=2018, month=5, day=30)
        )
        self.assertEqual(
            self.field.clean('2018-05-01 to 2018-05-30'),
            date_tuple
        )

    def test_to_python(self):
        date_tuple = (
            datetime.date(year=2018, month=5, day=1),
            datetime.date(year=2018, month=5, day=30)
        )

        self.assertEqual(
            self.field.to_python('2018-05-01 to 2018-05-30'),
            date_tuple
        )
        self.assertEqual(self.field.to_python(''), None)
        self.assertRaisesMessage(
            ValidationError,
            'Date range format invalid. Two dates are needed.',
            self.field.to_python, 'invalid'
        )
        self.assertRaisesMessage(
            ValidationError,
            'Date range format invalid. Try \'Y-m-d to Y-m-d\'',
            self.field.to_python, 'invalid to invalid'
        )
