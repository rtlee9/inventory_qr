from django.db import models
from django.urls import reverse


class UrlAction(models.Model):
    ACTION_TYPES = (
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    )
    action_type = models.CharField(
        max_length=10, choices=ACTION_TYPES, blank=False, null=False
    )
    long_url = models.URLField(max_length=400, blank=True, null=True)
    response_json = models.JSONField(blank=True, null=True)
    response_code = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    url_key = models.CharField(max_length=100, blank=False, null=False, default="")

    def __str__(self):
        return f"{self.action_type} ({self.id}): {self.url_key}"

    def was_successfull(self):
        return self.response_code == 200

    def get_absolute_url(self):
        return reverse("detail", kwargs={"pk": self.pk})
