from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from easy_pdf.rendering import render_to_pdf_response

client = Client()


class CreateTimesheetTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_details_form_view(self):
        response = client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='creator/home.html')

    def test_result_pdf_to_index_redirect(self):
        response = client.get(reverse('result'))

        self.assertRedirects(response, reverse('index'), status_code=302, target_status_code=200)

    def test_result_pdf_view(self):
        response = client.post(reverse('index'), data={
            'surname': 'Test',
            'first_name': 'Test',
            'days_worked': '2018-05-01 to 2018-05-30'
        })

        self.assertRedirects(response, reverse('result'), status_code=302, target_status_code=200)

        request = self.factory.get(reverse('result'))
        response = render_to_pdf_response(request, 'creator/timesheet.html', context={
            'surname': 'Testname',
            'first_name': 'Test',
            'unit_of_organization': 'Test',
            'header_date': '30.05.2018',
            'hours': 23,
            'timesheet_data': [
                {
                    'day': '2.',
                    'start': '08:00',
                    'end': '18:00',
                    'duration': '10:00',
                    'date': '02.05.18'
                }, {
                    'day': '5.',
                    'start': '08:00',
                    'end': '18:00',
                    'duration': '10:00',
                    'date': '05.05.18'
                }, {
                    'day': '6.',
                    'start': '10:00',
                    'end': '13:00',
                    'duration': '03:00',
                    'date': '06.05.18'
                }
            ],
            'total_hours': '23:00'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.content, bytes)
        self.assertEqual(response.content[:4], b'%PDF')
        self.assertIn('application/pdf', response._headers['content-type'])

    def test_invalid_form_no_surname(self):
        response = client.post(reverse('index'), data={
            'first_name': 'Test',
            'days_worked': '2018-05-01 to 2018-05-30'
        })

        self.assertFormError(response, 'form', 'surname', errors=['This field is required.'])

    def test_invalid_form_no_first_name(self):
        response = client.post(reverse('index'), data={
            'surname': 'Test',
            'days_worked': '2018-05-01 to 2018-05-30'
        })

        self.assertFormError(response, 'form', 'first_name', errors=['This field is required.'])

    def test_invalid_form_too_many_hours_for_working_days(self):
        response = client.post(reverse('index'), data={
            'first_name': 'Test',
            'surname': 'Test',
            'days_worked': '2018-05-01 to 2018-05-30',
            'hours': 1000
        })

        self.assertFormError(response, 'form', None, errors=['Too many hours for specified range of month'])

    def test_invalid_form_negative_hours(self):
        response = client.post(reverse('index'), data={
            'first_name': 'Test',
            'surname': 'Test',
            'days_worked': '2018-05-01 to 2018-05-30',
            'hours': -10
        })

        self.assertFormError(response, 'form', 'hours', errors=['Please provide a positive number of hours to work'])


class SubscribeTestCase(TestCase):
    def test_subscription_form_view(self):
        response = client.get(reverse('subscribe'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name='creator/subscription_subscribe.html')

    def test_subscription_success_view(self):
        response = client.post(reverse('subscribe'), data={
            'surname': 'Test',
            'first_name': 'Test',
            'email': 'test@testing.com'
        })

        self.assertRedirects(response, reverse('success'), status_code=302, target_status_code=200)

    def test_invalid_form_no_surname(self):
        response = client.post(reverse('subscribe'), data={
            'first_name': 'Test',
            'email': 'test@testing.com'
        })

        self.assertFormError(response, 'form', 'surname', errors=['This field is required.'])

    def test_invalid_form_no_first_name(self):
        response = client.post(reverse('subscribe'), data={
            'surname': 'Test',
            'email': 'test@testing.com'
        })

        self.assertFormError(response, 'form', 'first_name', errors=['This field is required.'])

    def test_invalid_form_no_email(self):
        response = client.post(reverse('subscribe'), data={
            'first_name': 'Test',
            'surname': 'Test',
        })

        self.assertFormError(response, 'form', 'email', errors=['This field is required.'])

    def test_invalid_form_invalid_email(self):
        response = client.post(reverse('subscribe'), data={
            'first_name': 'Test',
            'surname': 'Test',
            'email': 'invalid'
        })

        self.assertFormError(response, 'form', 'email', errors=['Enter a valid email address.'])
