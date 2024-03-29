from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Category, Khoroch
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
import datetime


# Create your views here.


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        expenses = Khoroch.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Khoroch.objects.filter(
            date__istartswith=search_str, owner=request.user) | Khoroch.objects.filter(
            description__icontains=search_str, owner=request.user) | Khoroch.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Khoroch.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
    }
    return render(request, 'khoroch/index.html', context)


@login_required(login_url='/authentication/login')
def add_khoroch(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }

    if request.method == 'GET':
        return render(request, 'khoroch/add-khoroch.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['khoroch_date']
        category = request.POST['category']

        if not amount:
            messages.error(request, 'Amount is Required')
            return render(request, 'khoroch/add-khoroch.html', context)

        if not description:
            messages.error(request, 'description is Required')
            return render(request, 'khoroch/add-khoroch.html', context)
        Khoroch.objects.create(owner=request.user, amount=amount,
                               date=date,
                               category=category,
                               description=description
                               )
        messages.success(request, 'Khoroch Added Succesfully')
        return redirect('khoroch')


def expense_edit(request, id):
    expense = Khoroch.objects.get(pk=id)
    categories = Category.objects.all()
    context = {
        'expense': expense,
        'values': expense,
        'categories': categories,
    }
    if request.method == 'GET':
        return render(request, 'khoroch/edit-expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['khoroch_date']
        category = request.POST['category']

        if not amount:
            messages.error(request, 'Amount is Required')
            return render(request, 'khoroch/edit-expense.html', context)

        if not description:
            messages.error(request, 'description is Required')
            return render(request, 'khoroch/edit-expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description
        expense.save()

        messages.success(request, 'Khoroch Updated Succesfully')
        return redirect('khoroch')


def delete_expense(request, id):
    expense = Khoroch.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense Deleted')
    return redirect('khoroch')


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_month_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Khoroch.objects.filter(owner=request.user, date__gte=six_month_ago, date__lte=todays_date)
    finalrep = {

    }

    def get_category(khoroch):
        return khoroch.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)

        for item in filtered_by_category:
            amount += item.amount

        return amount

    for x in expenses:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    return render(request, 'khoroch/stats.html')
