import pygal as pygal
from django.db.models import Q
from django.http import HttpResponseRedirect
from .models import Transaction, SubCategory, InputSource, Category, Rule
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import dateutil.parser
from .parsers.abstract import FileParser, remove_existing
from django.core.paginator import Paginator
from django.db.models import Sum
from datetime import datetime

def filter_index(request):
    try:
        startDate = request.POST['startDate']
        endDate = request.POST['endDate']
        source = request.POST['source']
        search = request.POST['search']
    except KeyError:
        # Redisplay the transaction voting form.
        return render(request, 'expenses/index.html', {})
    else:
        url = reverse('expenses:index') + "?startDate=" + startDate + "&endDate=" + endDate + '&source='+source\
              + '&search='+search
        return HttpResponseRedirect(url)


def get_datetime(date_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError) as e:
        return None
    else:
        return date


def index(request):
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    source = request.GET.get('source')
    search = request.GET.get('search')
    transaction_list = Transaction.objects

    if get_datetime(start_date) is not None:
        transaction_list = transaction_list.filter(date__gte=get_datetime(start_date))
    if get_datetime(end_date) is not None:
        transaction_list = transaction_list.filter(date__lte=get_datetime(end_date))
    if source != "all" and source != "None" and source is not None:
        transaction_list = transaction_list.filter(source_id=int(source))
    if search != '' and search is not None and search != 'None':
        transaction_list = transaction_list.filter(Q(merchant__icontains=search) | Q(comment__icontains=search))
    transaction_list = transaction_list.order_by('-date')

    paginator = Paginator(transaction_list, 15) # Show 25 contacts per page
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    input_source_list = InputSource.objects.all()
    context = {'transactions':  transactions,
               'startDate': start_date, 'endDate': end_date,
               'inputSources': input_source_list,
               'source': source,
               'search': search}

    return render(request, 'expenses/index.html', context)


def add_txn(request):
    return render(request, 'expenses/add.html', {'subcategories': SubCategory.objects.all()})


def add_txn_post(request):
    return render(request, 'expenses/add.html', {'error_message': "Not Supported",})
    try:
        text = request.POST['text']
        date = request.POST['date']
        amount = request.POST['amount']
        subCatagory_id = request.POST['subcategory_id']
    except (KeyError, SubCategory.DoesNotExist):
        # Redisplay the transaction voting form.
        return render(request, 'expenses/add.html', { 'error_message': "All fields mandatory",})
    else:
        transaction = Transaction(text=text, date=dateutil.parser.parse(date), amount=amount,
                                  subcatagory=SubCategory.objects.get(pk=subCatagory_id) )
        transaction.save()
        return HttpResponseRedirect(reverse('expenses:index'))


def add_txn_file_post(request):
    try:
        uploaded_file = request.FILES['txns_file']
    except (KeyError, SubCategory.DoesNotExist):
        # Redisplay the transaction voting form.
        return render(request, 'expenses/add.html', { 'error_message': "All fields mandatory",})
    else:
        parser = FileParser().factory(uploaded_file)
        if parser is None:
            return render(request, 'expenses/add.html', {'error_message': "Unknown file format",})
        transactions = parser.get_transactions(uploaded_file)
        transactions = remove_existing(transactions)
        for txn in transactions:
            txn.save()
        return HttpResponseRedirect(reverse('expenses:index'))


def detail(request, txn_id):
    transaction = get_object_or_404(Transaction, pk=txn_id)
    return render(request, 'expenses/detail.html', {'transaction': transaction,
                                                    'subCatagories':SubCategory.objects.all()})


def edit_txn(request, txn_id):
    transaction = get_object_or_404(Transaction, pk=txn_id)
    try:
        selected_subCatagory_id = request.POST['SubCatagory']
    except (KeyError, SubCategory.DoesNotExist):
        # Redisplay the transaction voting form.
        return render(request, 'expenses/detail.html', {
            'transaction': transaction,
            'error_message': "You didn't select a choice.", })
    else:
        transaction.subcategory = SubCategory.objects.get(pk=selected_subCatagory_id)
        transaction.save()
        return HttpResponseRedirect(reverse('expenses:index'))


def stats(request):

    date_list = [datetime.today() - dateutil.relativedelta.relativedelta(months=x) for x in range(11, -1, -1)]

    sum_list = []
    for date in date_list:
        sum_list.append(Transaction.objects.filter(date__year=date.year, date__month=date.month).aggregate(Sum('amount'))['amount__sum'])

    str_month_list = [datetime.strftime(x, '%b %Y') for x in date_list]

    line_chart = pygal.Bar()
    line_chart.x_labels = str_month_list
    line_chart.add('amount', sum_list)

    chart = line_chart.render_data_uri()
    context = {'chart': chart}

    return render(request, 'expenses/stats.html', context)


def index_action(request):
    marked_transactions = request.POST.getlist('marked_checkbox')
    startDate = request.POST['startDate']
    endDate = request.POST['endDate']
    source = request.POST['source']

    if request.POST['action'] == 'delete':
        for marked in marked_transactions:
            transaction = Transaction.objects.get(pk=marked)
            transaction.delete()
    url = reverse('expenses:index') + "?startDate=" + startDate + "&endDate=" + endDate + '&source=' + source
    return HttpResponseRedirect(url)


def categories(request):
    sub_categories = SubCategory.objects.all()
    categories = Category.objects.all()
    context = {
        'sub_categories': sub_categories,
        'categories': categories
    }

    return render(request, 'expenses/categories.html', context)


def categories_add(request):
    try:
        text = request.POST['text']
    except (KeyError):
        # Redisplay the transaction voting form.
        return render(request, 'expenses/categories', { 'error_message': "All fields mandatory",})
    else:
        if text != '':
            category = Category(text=text)
            category.save()
        return HttpResponseRedirect(reverse('expenses:categories'))


def sub_categories_add(request):
    try:
        text = request.POST['text']
        category_id = request.POST['category_id']
        category = Category.objects.get(pk=category_id)
    except (KeyError, Category.DoesNotExist):
        # Redisplay the transaction voting form.
        return render(request, 'expenses/categories', { 'error_message': "All fields mandatory",})
    else:
        if text != '':
            sub_category = SubCategory(text=text, category=category)
            sub_category.save()
        return HttpResponseRedirect(reverse('expenses:categories'))


def rules(request):
    rules = Rule.objects.all()
    context = {'rules': rules}
    return render(request, 'expenses/rules.html', context)


def categories_action(request):
    marked_categories = request.POST.getlist('marked_checkbox')
    if request.POST['action'] == 'delete':
        for marked in marked_categories:
            category = Category.objects.get(pk=marked)
            category.delete()
    return HttpResponseRedirect(reverse('expenses:categories'))

def sub_categories_action(request):
    marked_sub_categories = request.POST.getlist('marked_checkbox_sub')
    if request.POST['action'] == 'delete':
        for marked in marked_sub_categories:
            sub_category = SubCategory.objects.get(pk=marked)
            sub_category.delete()
    return HttpResponseRedirect(reverse('expenses:categories'))
