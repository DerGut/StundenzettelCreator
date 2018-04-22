from django.conf.urls import url

from creator.views import DetailsFormView, ResultPdfView

urlpatterns = [
    url(r'^$', DetailsFormView.as_view(), name='index'),
    url(r'^result', ResultPdfView.as_view(), name='result'),
]
