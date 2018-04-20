from django.conf.urls import url

from creator.views import DummyView

urlpatterns = [
    url(r'^$', DummyView.as_view(), name='index')
]
