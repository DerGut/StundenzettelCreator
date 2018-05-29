from django.conf.urls import url

from creator import views

urlpatterns = [
    url(r'^$', views.DetailsFormView.as_view(), name='index'),
    url(r'^result/', views.ResultPdfView.as_view(), name='result'),
    url(r'^subscribe/', views.SubscriptionFormView.as_view(), name='subscribe'),
    url(r'^success/', views.SubscriptionSuccessView.as_view(), name='success'),
    url(r'^unsubscribe/(?P<token>[\w.\-]+)', views.unsubscribe, name='unsubscribe')
]
