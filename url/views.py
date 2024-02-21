from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse

from . import models

detail_view = DetailView.as_view(model=models.UrlAction)
list_view = ListView.as_view(model=models.UrlAction)

class Create(CreateView):
    model=models.UrlAction
    fields=["action_type", "long_url", "url_key"]

    def get_success_url(self):
        url = reverse('detail', kwargs={'pk': self.object.pk})
        return url + '?source=create'