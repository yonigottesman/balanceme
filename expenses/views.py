from django.http import HttpResponse, HttpResponseRedirect
from .models import Transaction, SubCategory
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import dateutil.parser
from .parsers.abstract import FileParser

def index(request):
    latest_txn_list = Transaction.objects.order_by('-date')[:50]
    context = { 'latest_txn_list': latest_txn_list, }
    return render(request, 'expenses/index.html', context)

def add_txn(request):
    return render(request, 'expenses/add.html', {'subcategories':SubCategory.objects.all()})

def add_txn_post(request):
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
        uploaded_file = request.FILES['txns_file'].read()
    except (KeyError, SubCategory.DoesNotExist):
        # Redisplay the transaction voting form.
        return render(request, 'expenses/add.html', { 'error_message': "All fields mandatory",})
    else:
        parser = FileParser.factory(uploaded_file)
        transactions = parser.get_transactions(uploaded_file)
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

