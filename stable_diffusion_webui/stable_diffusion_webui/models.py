from django.db import models
from django.core.files.storage import FileSystemStorage 
import os



class GenerateRequest(models.Model):
    request_body = models.JSONField()
    create_at = models.DateTimeField(auto_now_add=True)


class Prompt(models.Model):
    request = models.ForeignKey(GenerateRequest, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.FilePathField()
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "stable_diffusion_webui"

    def media_url(self):
        store = FileSystemStorage()
        filename = os.path.basename(self.image)
        url = store.url(filename)
        return url

