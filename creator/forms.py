import datetime

from django import forms
from django.core.exceptions import ValidationError

today = datetime.date.today()
defaults = {
    'hours': 23,
    'unit_of_organisation': '<your organisation>',
    'days_of_week': [0, 1, 2, 3, 4],
    'start_hour': 8,
    'end_hour': 18,
    'max_hours': 6,
    'state': 'NI',
    'month': today.month,
    'year': today.year,
    'first_day_of_month': 1,
    'last_day_of_month': today.day - 1
}


class DetailsForm(forms.Form):
    # Important details
    name = forms.CharField(help_text='Name of the employee')
    first_name = forms.CharField(help_text='First name of the employee')
    hours = forms.IntegerField(required=False, initial=defaults['hours'])
    unit_of_organisation = forms.CharField(required=False, initial=defaults['unit_of_organisation'])

    # Advanced details
    first_day_of_month = forms.DateField(
        required=False,
        help_text='First day of the month that should be used (defaults to beginning of month)'
    )
    last_day_of_month = forms.DateField(
        required=False,
        help_text='Last day of the month that should be used (defaults to yesterday)'
    )
    start_hour = forms.IntegerField(
        required=False,
        initial=defaults['start_hour'],
        widget=forms.TimeInput()
    )
    end_hour = forms.IntegerField(
        required=False,
        initial=defaults['end_hour'],
        widget=forms.TimeInput()
    )
    max_hours = forms.IntegerField(
        required=False,
        initial=defaults['max_hours']
    )

    def clean(self):
        cleaned_data = super().clean()

        # Validate fdom and ldom
        fdom = cleaned_data.get('first_day_of_month')
        ldom = cleaned_data.get('last_day_of_month')
        if fdom or ldom:
            if fdom and fdom:
                if fdom.year != ldom.year:
                    raise ValidationError(
                        'First day of month and last of month are not within the same year',
                        code='invalid')
                if fdom.month != ldom.month:
                    raise ValidationError(
                        'First day of month and last of month are not within the same month',
                        code='invalid')

            # Set the year and month to that specified by fdom and ldom
            if fdom:
                cleaned_data['year'] = fdom.year
                cleaned_data['month'] = fdom.month
            else:
                cleaned_data['year'] = ldom.year
                cleaned_data['month'] = ldom.month

        # Else, set the year and month to current
        else:
            cleaned_data['year'] = defaults['year']
            cleaned_data['month'] = defaults['month']

        # Set all the default values
        for field in cleaned_data.items():
            if not field[1]:
                if field[0] in defaults.keys():
                    cleaned_data[field[0]] = defaults[field[0]]
                else:
                    raise ValidationError(
                        'Please fill out: %(field)s',
                        params={'field': field[0]},
                        code='empty'
                    )

        cleaned_data['state'] = defaults['state']
        cleaned_data['days_of_week'] = defaults['days_of_week']
