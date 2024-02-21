import logging
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django import forms


from utils.url import create, update, delete

logger = logging.getLogger(__name__)

from . import models

detail_view = login_required(DetailView.as_view(model=models.UrlAction))
list_view = login_required(ListView.as_view(model=models.UrlAction))

url_actions = {
    "create": create,
    "update": update,
    "delete": delete,
}


class CreateForm(forms.ModelForm):
    class Meta:
        model = models.UrlAction
        fields = ["action_type", "long_url", "url_key"]

    def clean_long_url(self):
        data = self.cleaned_data
        if data["action_type"] in ("create", "update") and not data["long_url"]:
            raise forms.ValidationError("Long URL is required for this action type.")
        return data.get("long_url")


class Create(CreateView):
    model = models.UrlAction
    form_class = CreateForm

    def get_success_url(self):
        # perform the url action
        action = url_actions[self.object.action_type]
        if not self.object.was_successfull():
            logger.error("Error creating UrlAction object: %s", self.object)
        kwargs = {"key": self.object.url_key}
        if action in (create, update):
            kwargs["long_url"] = self.object.long_url
        response = action(**kwargs)
        logger.info("Response: %s", response)
        if action== update:
            # handle two sets of responses: one for create and one for delete
            self.object.response_code = max([item['response_code'] for item in response])
            self.object.response_json = [item['response_json'] for item in response]
        else:
            self.object.response_code = response['response_code']
            self.object.response_json = response['response_json']
        self.object.save()

        # get success url
        url = reverse("detail", kwargs={"pk": self.object.pk})
        return url + "?source=create"
