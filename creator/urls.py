from django.conf.urls import url

from creator.views import DetailsFormView, ResultPdfView, SubscriptionFormView

urlpatterns = [
    url(r'^$', DetailsFormView.as_view(), name='index'),
    url(r'^result', ResultPdfView.as_view(), name='result'),
    url(r'^subscribe', SubscriptionFormView.as_view(), name='subscribe'),
]
