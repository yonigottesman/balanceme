from django.http import HttpResponse
from .models import Transaction
from django.shortcuts import render, get_object_or_404




def index(request):
    latest_txn_list = Transaction.objects.order_by('-txn_date')[:5]
    context = { 'latest_txn_list': latest_txn_list, }
    return render(request, 'expenses/index.html', context)



def detail(request, txn_id):
    transaction = get_object_or_404(Transaction, pk=txn_id)
    return render(request, 'expenses/detail.html', {'transaction': transaction})


def results(request, txn_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % txn_id)

def vote(request, txn_id):
    return HttpResponse("You're voting on question %s." % txn_id)

