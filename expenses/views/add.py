import time
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from expenses.models import SubCategory
from expenses.parsers.abstract import FileParser, remove_existing


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
        ts = time.time()
        parser = FileParser().factory(uploaded_file)
        #print("after factory: " + str(time.time() - ts))
        if parser is None:
            return render(request, 'expenses/add.html', {'error_message': "Unknown file format",})
        transactions = parser.get_transactions(uploaded_file, request.user)
        print("after get: " + str(time.time() - ts))
        transactions = remove_existing(transactions)
        #print("after remove: " + str(time.time() - ts))
        for txn in transactions:
            txn.save()
        #print("after save: " + str(time.time() - ts))
        te = time.time()
        print("total time: " + str(te - ts))

        return HttpResponseRedirect(reverse('expenses:index'))
