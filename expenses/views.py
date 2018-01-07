from django.http import HttpResponse
from .models import Transaction

def index(request):
    latest_question_list = Transaction.objects.order_by('-pub_date')[:5]
    output = ', '.join([q.question_text for q in latest_question_list])
    return HttpResponse(output)


def detail(request, txn_id):
    return HttpResponse("You're looking at question %s." % txn_id)

def results(request, txn_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % txn_id)

def vote(request, txn_id):
    return HttpResponse("You're voting on question %s." % txn_id)

