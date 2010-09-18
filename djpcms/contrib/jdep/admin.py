from django.contrib import admin
import models

admin.site.register(models.DeploySite, list_display=['site', 'user', 'created', 'comment'])