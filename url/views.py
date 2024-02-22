import logging
from django.views import generic
from django.urls import reverse
from django import forms


from utils.url import create, update, delete

logger = logging.getLogger(__name__)

from . import models

detail_view = generic.DetailView.as_view(model=models.UrlAction)
list_view = generic.ListView.as_view(model=models.UrlAction)

url_actions = {
    "create": create,
    "update": update,
    "delete": delete,
}


class MostRecentView(generic.ListView):
    model = models.UrlAction
    ordering = ["pk"]

    def get_queryset(self):
        qs = super().get_queryset()
        latest_id_per_url_key = (
            qs.order_by("url_key", "-timestamp").distinct("url_key").values_list("id")
        )
        return qs.filter(pk__in=latest_id_per_url_key).filter(
            action_type__in=["create", "update"]
        )


class CreateForm(forms.ModelForm):
    class Meta:
        model = models.UrlAction
        fields = ["action_type", "long_url", "url_key"]

    def clean_long_url(self):
        data = self.cleaned_data
        if data["action_type"] in ("create", "update") and not data["long_url"]:
            raise forms.ValidationError("Long URL is required for this action type.")
        return data.get("long_url")


class Create(generic.CreateView):
    model = models.UrlAction
    form_class = CreateForm

    def get_initial(self):
        initial = super().get_initial().copy()
        initial["action_type"] = self.request.GET.get("action_type")
        initial["url_key"] = self.request.GET.get("url_key")
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user  # set user foreign key
        return super().form_valid(form)

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
        if action == update:
            # handle two sets of responses: one for create and one for delete
            self.object.response_code = max(
                [item["response_code"] for item in response]
            )
            self.object.response_json = [item["response_json"] for item in response]
        else:
            self.object.response_code = response["response_code"]
            self.object.response_json = response["response_json"]
        self.object.save()

        # get success url
        url = reverse("detail", kwargs={"pk": self.object.pk})
        return url + "?source=create"
