import datetime
import logging

import itsdangerous
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from easy_pdf.views import PDFTemplateView

from creator.forms import TimesheetWithDateRangeForm, SubscriptionForm
from creator.models import Subscription

logger = logging.getLogger(__name__)


class DetailsFormView(FormView):
    template_name = 'creator/home.html'
    form_class = TimesheetWithDateRangeForm
    success_url = '/result/'

    def form_valid(self, form):
        self.request.session['data'] = form.cleaned_data

        return super(DetailsFormView, self).form_valid(form)


class ResultPdfView(PDFTemplateView):
    template_name = 'creator/timesheet.html'

    def get_context_data(self, **kwargs):
        try:
            data = self.request.session['data']
        except KeyError:
            return None

        return super(ResultPdfView, self).get_context_data(pagesize='A4', **data)

    def render_to_response(self, context, **response_kwargs):
        if not context:
            return redirect('index')

        return super(ResultPdfView, self).render_to_response(context, **response_kwargs)


class SubscriptionFormView(FormView):
    template_name = 'creator/subscription_subscribe.html'
    form_class = SubscriptionForm
    success_url = '/success/'

    def form_valid(self, form):
        subscription = Subscription.objects.create(
            email=form.cleaned_data['email'],
            hours=form.cleaned_data['hours'],
            unit_of_organisation=form.cleaned_data['unit_of_organisation'],
            first_name=form.cleaned_data['first_name'],
            surname=form.cleaned_data['surname']
        )

        self.request.session['subscription_id'] = subscription.pk

        return super().form_valid(form)


class SubscriptionSuccessView(DetailView):
    template_name = 'creator/subscription_success.html'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Subscription, pk=self.request.session['subscription_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        date = Subscription.objects.date_of_subscription(datetime.datetime.today())
        context.update({'next_timesheet': date.strftime('%a %-d of %B')})

        return context

    def get(self, request, *args, **kwargs):
        if not self.request.session.get('subscription_id'):
            return redirect('subscribe')

        return super().get(request, *args, **kwargs)


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
