from django.contrib import admin

# Register your models here.
from . import models


@admin.register(models.CustomUser)
class UserAdmin(admin.ModelAdmin):
    pass
