from django.contrib import admin
from .models import Khoroch, Category


# Register your models here.

class KhorochAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'owner', 'category', 'date')
    search_fields = ('description', 'category', 'date')


admin.site.register(Khoroch, KhorochAdmin)
admin.site.register(Category)
