from django.contrib import admin
from .models import UserIncome, Source


# Register your models here.

class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'source', 'owner', 'date')
    search_fields = ('description', 'source', 'date')


admin.site.register(UserIncome, IncomeAdmin)
admin.site.register(Source)
