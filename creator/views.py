import logging

import itsdangerous
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from easy_pdf.views import PDFTemplateView

from creator.exceptions import TimesheetCreationError
from creator.forms import DetailsForm, SubscriptionForm
from creator.models import Subscription
from creator.timesheet import generate_timesheet_data

logger = logging.getLogger(__name__)


class DetailsFormView(FormView):
    template_name = 'creator/home.html'
    form_class = DetailsForm
    success_url = '/result/'

    def form_valid(self, form):
        self.request.session['details'] = form.cleaned_data

        return super(DetailsFormView, self).form_valid(form)


class SubscriptionFormView(FormView):
    template_name = 'creator/subscription_subscribe.html'
    form_class = SubscriptionForm
    success_url = '/success/'

    def form_valid(self, form):
        subscription = Subscription.objects.create(
            email=form.cleaned_data['email'],
            first_send_date=form.cleaned_data['first_send_date'],
            next_send_date=form.cleaned_data['first_send_date'],
            hours=form.cleaned_data['hours'],
            unit_of_organisation=form.cleaned_data['unit_of_organisation'],
            first_name=form.cleaned_data['first_name'],
            surname=form.cleaned_data['surname']
        )

        self.request.session['subscription_id'] = subscription.pk

        return super().form_valid(form)


class SuccessView(DetailView):
    template_name = 'creator/subscription_success.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Subscription, pk=self.request.session['subscription_id']
        )


def unsubscribe(request, token):
    signer = itsdangerous.URLSafeTimedSerializer(secret_key=settings.SECRET_KEY)
    max_age = 60 * 60 * 24 * 7  # Seven days till the link expires

    try:
        subscription_id = signer.loads(token, max_age=max_age)
        get_object_or_404(Subscription, pk=subscription_id).delete()
        context = {
            'status': 'success',
        }
    except itsdangerous.SignatureExpired:
        context = {
            'status': 'failure',
            'reason': 'expired'
        }
        logger.warning('Unsubscribe link expired')
    except itsdangerous.BadTimeSignature as e:
        logger.error('Wrong signature format [{}]: {}'.format(e, token))
        context = {
            'status': 'failure',
            'reason': 'tampered'
        }
    except itsdangerous.BadSignature as e:
        context = {
            'status': 'failure',
            'reason': 'tampered'
        }
        logger.error('Tampering with unsubscribe link detected [{}]: {}'.format(e, token))

        encoded_payload = e.payload
        if encoded_payload is not None:
            try:
                decoded_payload = signer.load_payload(encoded_payload)
                logger.error('Payload was {}'.format(decoded_payload))
            except itsdangerous.BadData:
                pass

    return render(request, 'creator/subscription_unsubscribe.html', context=context)


class ResultPdfView(PDFTemplateView):
    template_name = 'creator/timesheet.html'

    def get_context_data(self, **kwargs):
        try:
            timesheet_data, header_date, total_hours = generate_timesheet_data(
                self.request.session.get('details'))
        except TimesheetCreationError as e:
            # TODO: Show error view
            pass

        return super(ResultPdfView, self).get_context_data(
            pagesize='A4',
            details=self.request.session.get('details'),
            data=timesheet_data,
            header_date=header_date,
            total_hours=total_hours
        )
