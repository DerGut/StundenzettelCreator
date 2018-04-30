from django.conf.urls import url

from creator.views import DetailsFormView, ResultPdfView, SubscriptionFormView, SuccessView, UnsubscribeView

urlpatterns = [
    url(r'^$', DetailsFormView.as_view(), name='index'),
    url(r'^result/', ResultPdfView.as_view(), name='result'),
    url(r'^subscribe/', SubscriptionFormView.as_view(), name='subscribe'),
    url(r'^success/', SuccessView.as_view(), name='success'),
    url(r'^unsubscribe/(?P<hash>[*]{32})/', UnsubscribeView.as_view(), name='unsubscribe')
]
