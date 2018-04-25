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
        # If any of (None, '', [], (), {})
        if value in self.empty_values:
            return None

        date1, date2 = value.split(' to ')
        try:
            date1 = super(DateRangeField, self).to_python(date1)
            date2 = super(DateRangeField, self).to_python(date2)
        except ValidationError:
            raise ValidationError(self.error_messages['invalid'], code='invalid')

        return date1, date2

    def strptime(self, value, format):
        return datetime.datetime.strptime(force_str(value), format).date()
