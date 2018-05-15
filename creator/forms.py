import datetime

from django import forms
from django.core.exceptions import ValidationError

from creator.exceptions import TimesheetCreationError
from creator.fields import DateRangeField
from creator.timesheet import generate_timesheet_data

today = datetime.date.today()
defaults = {
    'hours': 23,
    'unit_of_organisation': 'Fachbereich 08',
    'month': today.month,
    'year': today.year,
    'first_day_of_month': 1,
    'last_day_of_month': today.day - 1,
    'days_worked': None
}

placeholder_daterange = '{} to {}'.format(
    datetime.datetime(
        year=today.year,
        month=today.month,
        day=1
    ).strftime('%B %-d'),
    (today - datetime.timedelta(days=1)).strftime('%B %-d')
)


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
            'placeholder': placeholder_daterange
        })
    )

    def clean_first_name(self):
        data = self.cleaned_data['first_name']

        return data

    def clean_surname(self):
        data = self.cleaned_data['surname']

        return data

    def clean_unit_of_organisation(self):
        if self.cleaned_data['unit_of_organisation']:
            data = self.cleaned_data['unit_of_organisation']
        else:
            data = defaults['unit_of_organisation']

        return data

    def clean_hours(self):
        if self.cleaned_data['hours']:
            data = self.cleaned_data['hours']
            if data < 0:
                raise ValidationError('Please provide a positive number of hours to work', code='invalid')
        else:
            data = defaults['hours']

        return data

    def clean_days_worked(self):
        if self.cleaned_data['days_worked']:
            fdom, ldom = self.cleaned_data['days_worked']

            if fdom.year != ldom.year:
                raise ValidationError(
                    'First day and last day are not within the same year',
                    code='invalid')
            if fdom.month != ldom.month:
                raise ValidationError(
                    'First day and last day are not within the same month',
                    code='invalid')

            self.cleaned_data['year'] = fdom.year
            self.cleaned_data['month'] = fdom.month
            self.cleaned_data['first_day_of_month'] = fdom.day
            self.cleaned_data['last_day_of_month'] = ldom.day
        else:
            self.cleaned_data['year'] = defaults['year']
            self.cleaned_data['month'] = defaults['month']
            self.cleaned_data['first_day_of_month'] = defaults['first_day_of_month']
            self.cleaned_data['last_day_of_month'] = defaults['last_day_of_month']

        # Fix for some weird json serialization error
        del self.cleaned_data['days_worked']

    def _post_clean(self):
        data = self.cleaned_data

        # TODO: This is stupid. But the add_error method requires a ValidationError object
        try:
            try:
                # Generate the timesheet data
                timesheet_data, header_date, total_hours = generate_timesheet_data(
                    data['year'], data['month'], data['first_day_of_month'], data['last_day_of_month'], data['hours']
                )
                data.update({
                    'timesheet_data': timesheet_data,
                    'header_date': header_date,
                    'total_hours': total_hours
                })

                self.cleaned_data = data
            except KeyError:
                pass
            except TimesheetCreationError as tce:
                raise ValidationError(tce)
        except ValidationError as ve:
            self.add_error(None, ve)

        return data


class SubscriptionForm(DetailsForm):
    email = forms.EmailField(required=True)
    first_send_date = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'datepicker',
        })
    )
