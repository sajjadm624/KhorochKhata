from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name="khoroch"),
    path('add-khoroch', views.add_khoroch, name="add-khoroch"),
    path('edit-expense/<int:id>', views.expense_edit, name="expense-edit"),
    path('delete-expense/<int:id>', views.delete_expense, name="expense-delete"),
    path('search-expenses', csrf_exempt(views.search_expenses), name="search_expenses"),
    path('expense-category-summary', views.expense_category_summary, name="expense-category-summary"),
    path('stats', views.stats_view, name="stats"),
]