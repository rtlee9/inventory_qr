from django.db import models
from django.urls import reverse
from utils.qr import gen_qr


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
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.action_type} ({self.id}): {self.url_key}"

    def was_successfull(self):
        return self.response_code == 200

    def get_absolute_url(self):
        return reverse("detail", kwargs={"pk": self.pk})

    @property
    def long_url_cleaned(self):
        """Remove GET parameters from URL"""
        if not self.long_url:
            return
        return self.long_url.split("?")[0]

    @property
    def qr_url(self):
        return gen_qr(f"https://aws3.link/{self.url_key}")

    @property
    def qr_url_small(self):
        return gen_qr(f"https://aws3.link/{self.url_key}", 70)
