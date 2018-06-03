import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms.fields import BaseTemporalField
from django.utils.encoding import force_str
from django.utils.formats import get_format_lazy
from django.utils.translation import ugettext_lazy as _


class DateRangeField(BaseTemporalField):
    widget = forms.DateInput
    input_formats = get_format_lazy('DATE_INPUT_FORMATS')
    default_error_messages = {
        'invalid': _('Enter a valid date range.'),
    }

    def to_python(self, value):
        """Takes the raw form input and translates it to two python datetime objects"""
        # If any of (None, '', [], (), {})
        if value in self.empty_values:
            return None

        try:
            date1, date2 = value.split(' to ')

            date1 = super(DateRangeField, self).to_python(date1)
            date2 = super(DateRangeField, self).to_python(date2)
        except ValueError:
            raise ValidationError('Date range format invalid. Two dates are needed.')
        except ValidationError:
            raise ValidationError('Date range format invalid. Try \'Y-m-d to Y-m-d\'', code='invalid')

        return date1, date2

    def strptime(self, value, format):
        """Overwrites the builtin to parse a datetime out of str"""
        return datetime.datetime.strptime(force_str(value), format).date()
