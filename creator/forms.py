import datetime

from django import forms
from django.core.exceptions import ValidationError

from creator.fields import DateRangeField

today = datetime.date.today()
defaults = {
    'hours': 23,
    'unit_of_organisation': 'Fachbereich 08',
    'days_of_week': [0, 1, 2, 3, 4],
    'start_hour': 8,
    'end_hour': 18,
    'max_hours': 6,
    'state': 'NI',
    'month': today.month,
    'year': today.year,
    'first_day_of_month': 1,
    'last_day_of_month': today.day - 1,
    'date_range': '{} to {}'.format(
        datetime.datetime(year=today.year, month=today.month, day=1).strftime('%B %-d'),
        (today - datetime.timedelta(days=1)).strftime('%B %-d')
    ),
    'days_worked': None
}


class DetailsForm(forms.Form):
    # Important details
    surname = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '<your name>'})
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '<your first name>'})
    )

    # Advanced details
    unit_of_organisation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': defaults['unit_of_organisation']})
    )
    hours = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': defaults['hours']})
    )
    days_worked = DateRangeField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'daterangepicker',
            'placeholder': defaults['date_range']
        })
    )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['days_worked']:
            fdom, ldom = cleaned_data['days_worked']

            if fdom.year != ldom.year:
                raise ValidationError(
                    'First day and last day are not within the same year',
                    code='invalid')
            if fdom.month != ldom.month:
                raise ValidationError(
                    'First day and last day are not within the same month',
                    code='invalid')

            cleaned_data['year'] = fdom.year
            cleaned_data['month'] = fdom.month
            cleaned_data['first_day_of_month'] = fdom.day
            cleaned_data['last_day_of_month'] = ldom.day
        else:
            cleaned_data['year'] = defaults['year']
            cleaned_data['month'] = defaults['month']
            cleaned_data['first_day_of_month'] = defaults['first_day_of_month']
            cleaned_data['last_day_of_month'] = defaults['last_day_of_month']

        # Fix for some weird json serialization error
        del cleaned_data['days_worked']

        # Set all the default values
        for field_name, value in cleaned_data.items():
            if not value:
                if field_name in defaults.keys():
                    cleaned_data[field_name] = defaults[field_name]
                else:
                    raise ValidationError(
                        'Please fill out: %(field)s',
                        params={'field': field_name},
                        code='empty'
                    )

        cleaned_data['state'] = defaults['state']
        cleaned_data['days_of_week'] = defaults['days_of_week']
        cleaned_data['start_hour'] = defaults['start_hour']
        cleaned_data['end_hour'] = defaults['end_hour']
        cleaned_data['max_hours'] = defaults['max_hours']
