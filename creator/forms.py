from django import forms


class DetailsForm(forms.Form):
    name = forms.CharField(
        error_messages={
            'required': 'Please enter the name that should be displayed on the timesheet'
        }, widget=forms.TextInput(attrs={'placeholder': 'Max'})
    )
    firstname = forms.CharField()
    hours = forms.IntegerField()

    last_day_month = forms.DateField(required=False, label='Last day of the month')
    start_time = forms.TimeField(required=False)
    end_time = forms.TimeField(required=False)
    max_hours = forms.IntegerField(required=False)
