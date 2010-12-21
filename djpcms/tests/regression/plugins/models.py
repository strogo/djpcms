from django.db import models


class SearchModel(models.Model):
    name = models.CharField(max_length = 200)
    description = models.TextField()