from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Condition)
admin.site.register(models.Symptom)
