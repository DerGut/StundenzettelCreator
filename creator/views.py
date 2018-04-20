# Create your views here.
from django.views import generic


class DummyView(generic.TemplateView):
    template_name = 'home.html'


