
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from expenses.models import SubCategory, Transaction
from expenses.parsers.abstract import FileParser


def add(request):
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
        return render(request, 'expenses/add.html', {'error_message': "All fields mandatory"})
    else:

        parser = FileParser().factory(uploaded_file)

        if parser is None:
            return render(request, 'expenses/add.html', {'error_message': "Unknown file format",})
        transactions = parser.get_transactions(uploaded_file, request.user)
        if transactions is None:
            return render(request, 'expenses/add.html', {'error_message': "Unknown file format",})
        transactions = remove_existing(transactions)

        for txn in transactions:
            txn.save()

        return HttpResponseRedirect(reverse('expenses:index'))


# TODO check efficiency of this function
def remove_existing(new_transactions):
    if len(new_transactions) is 0:
        return new_transactions

    without_duplicates = []
    for transaction in new_transactions:

        found = Transaction.objects \
            .filter(owner=transaction.owner) \
            .filter(comment=transaction.comment)\
            .filter(merchant=transaction.merchant)\
            .filter(amount=transaction.amount)\
            .filter(source=transaction.source)\
            .filter(date=transaction.date)

        if len(found) == 0:
            without_duplicates.append(transaction)

    return without_duplicates
