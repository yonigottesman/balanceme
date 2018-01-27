import pygal as pygal
from django.http import HttpResponseRedirect
from .models import Transaction, SubCategory, InputSource
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import dateutil.parser
from .parsers.abstract import FileParser, remove_existing
from django.core.paginator import Paginator
import datetime
from django.db.models import Sum


def filter_index(request):
    try:
        startDate = request.POST['startDate']
        endDate = request.POST['endDate']
        source = request.POST['source']
    except KeyError:
        # Redisplay the transaction voting form.
        return render(request, 'expenses/index.html', {})
    else:
        url = reverse('expenses:index') + "?startDate=" + startDate + "&endDate=" + endDate + '&source='+source
        return HttpResponseRedirect(url)


def index(request):
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    source = request.GET.get('source')
    end_date_input_value = str(datetime.date.today())
    start_date_input_value = str((datetime.date.today() - datetime.timedelta(31)).replace(day=1))
    # transaction_list = []
    if (start_date is None or end_date is None) or (start_date == 'None' or end_date == 'None'):
        transaction_list = Transaction.objects.order_by('-date')

    else:
        start_date_input_value = start_date
        end_date_input_value = end_date
        transaction_list = Transaction.objects.filter(date__range=[start_date, end_date]).order_by('-date')  # year-month-day

    if source != "all" and source != "None" and source != None:
        transaction_list = transaction_list.filter(source_id=int(source))


    # transaction_list = Transaction.objects.order_by('-date')
    paginator = Paginator(transaction_list, 15) # Show 25 contacts per page
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    input_source_list = InputSource.objects.all()
    context = {'transactions':  transactions,
               'startDate': start_date, 'endDate': end_date,
               'inputSources': input_source_list,
               'startDateValue': start_date_input_value,
               'endDateValue': end_date_input_value,
               'source': source}

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
        transaction.subcatagory = SubCategory.objects.get(pk=selected_subCatagory_id)
        transaction.save()
        return HttpResponseRedirect(reverse('expenses:index'))


def stats(request):

    date_list = [datetime.date.today() - dateutil.relativedelta.relativedelta(months=x) for x in range(11, -1, -1)]

    sum_list = []
    for date in date_list:
        sum_list.append(Transaction.objects.filter(date__year=date.year, date__month=date.month).aggregate(Sum('amount'))['amount__sum'])

    str_month_list = [datetime.date.strftime(x, '%b %Y') for x in date_list]

    line_chart = pygal.Bar()
    line_chart.x_labels = str_month_list
    line_chart.add('amount', sum_list)

    chart = line_chart.render_data_uri()
    context = {'chart': chart}

    return render(request, 'expenses/stats.html', context)