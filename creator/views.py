from django.views.generic.edit import FormView
from easy_pdf.views import PDFTemplateView

from creator.forms import DetailsForm


def queue_timesheet_rendering(form):
    pass


class DetailsFormView(FormView):
    template_name = 'home.html'
    form_class = DetailsForm
    success_url = '/result/'

    def form_valid(self, form):
        self.request.session['details'] = form.cleaned_data
        # queue_timesheet_rendering(form)
        return super(DetailsFormView, self).form_valid(form)


class ResultPdfView(PDFTemplateView):
    template_name = 'timesheet.html'

    def get_context_data(self, **kwargs):
        return super(ResultPdfView, self).get_context_data(
            pagesize='A4',
            details=self.request.session.get('details')
        )
