from django.test import TestCase

from creator.forms import TimesheetWithDateRangeForm, SubscriptionForm


class TimesheetDetailsFormTestCase(TestCase):
    def setUp(self):
        self.valid_data = {
            'surname': 'Test',
            'first_name': 'Test',
            'unit_of_organisation': 'Test',
            'hours': 23,
            'days_worked': '2018-05-01 to 2018-05-30'
        }

    def test_valid_input_data(self):
        form = TimesheetWithDateRangeForm(data=self.valid_data)

        self.assertTrue(form.is_valid())

    def test_no_surname_provided(self):
        del self.valid_data['surname']
        form = TimesheetWithDateRangeForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('surname'))

    def test_no_first_name_provided(self):
        del self.valid_data['first_name']
        form = TimesheetWithDateRangeForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('first_name'))

    def test_negative_hours(self):
        self.valid_data['hours'] = -23
        form = TimesheetWithDateRangeForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('hours'))
        self.assertEqual(
            form.errors['hours'],
            ['Please provide a positive number of hours to work']
        )

    def test_too_many_hours_for_days_worked(self):
        self.valid_data['hours'] = 1000
        form = TimesheetWithDateRangeForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        non_form_errors = form.non_field_errors()
        self.assertTrue(len(non_form_errors))
        self.assertEqual(
            non_form_errors[0],
            'Too many hours for specified range of month'
        )

    def test_working_days_range_not_in_same_month(self):
        self.valid_data['days_worked'] = '2018-05-15 to 2018-06-15'
        form = TimesheetWithDateRangeForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('days_worked'))
        self.assertEqual(
            form.errors['days_worked'],
            ['First day and last day are not within the same month']
        )

    def test_working_days_range_not_in_same_year(self):
        self.valid_data['days_worked'] = '2018-05-01 to 2019-05-30'
        form = TimesheetWithDateRangeForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('days_worked'))
        self.assertEqual(
            form.errors['days_worked'],
            ['First day and last day are not within the same year']
        )

    def test_working_days_range_not_in_same_year_and_month(self):
        self.valid_data['days_worked'] = '2018-12-15 to 2019-01-15'
        form = TimesheetWithDateRangeForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('days_worked'))
        self.assertEqual(
            form.errors['days_worked'],
            ['First day and last day are not within the same year']
        )


class SubscriptionFormTestCase(TestCase):
    def setUp(self):
        self.valid_data = self.valid_data = {
            'surname': 'Test',
            'first_name': 'Test',
            'unit_of_organisation': 'Test',
            'hours': 23,
            'days_worked': '2018-05-01 to 2018-05-30'
        }

    def test_valid_email(self):
        self.valid_data['email'] = 'test@bestemailaddressintheworld.com'
        form = SubscriptionForm(data=self.valid_data)

        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        self.valid_data['email'] = 'this_should_be_invalid'
        form = SubscriptionForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('email'))

    def test_no_email(self):
        form = SubscriptionForm(data=self.valid_data)

        self.assertFalse(form.is_valid())
        self.assertTrue(form.has_error('email'))
