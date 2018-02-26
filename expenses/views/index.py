from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import dateutil.parser

from expenses.common import get_datetime
from expenses.models import Transaction, Category, InputSource, SubCategory, Rule, RuleType

from django.core.paginator import Paginator

from datetime import datetime


def filter_index(request):
    try:
        start_date = request.POST['startDate']
        end_date = request.POST['endDate']
        source = request.POST['source']
        search = request.POST['search']
        category = request.POST['category']
    except KeyError:
        # Redisplay the transaction voting form.
        return render(request, 'expenses/index.html', {})
    else:
        url = reverse('expenses:index') + "?startDate=" + start_date + "&endDate=" + end_date + '&source='+source\
              + '&search='+search + '&category='+ category
        return HttpResponseRedirect(url)


# def get_datetime(date_str):
#     try:
#         date = datetime.strptime(date_str, '%Y-%m-%d')
#     except (ValueError, TypeError) as e:
#         return None
#     else:
#         return date


def index(request):

    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')
    source = request.GET.get('source')
    search = request.GET.get('search')
    category_id = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')

    transaction_list = Transaction.objects.filter(owner=request.user)

    if get_datetime(start_date) is not None:
        transaction_list = transaction_list.filter(date__gte=get_datetime(start_date))
    if get_datetime(end_date) is not None:
        transaction_list = transaction_list.filter(date__lte=get_datetime(end_date))
    if source != "all" and source != "None" and source is not None:
        source = int(source)
        transaction_list = transaction_list.filter(source_id=int(source))
    if search != '' and search is not None and search != 'None':
        transaction_list = transaction_list.filter(Q(merchant__icontains=search) | Q(comment__icontains=search))
    if category_id is not None and category_id != 'None' and category_id != '' and category_id != 'all':
        category = Category.objects.get(owner=request.user, pk=category_id)
        transaction_list = transaction_list.filter(subcategory__category=category)
        category_id = int(category_id)
    if subcategory_id != '' and subcategory_id is not None and subcategory_id!= 'None':
        subcategory = SubCategory.objects.get(owner=request.user, pk=subcategory_id)
        transaction_list = transaction_list.filter(subcategory=subcategory)

    transaction_list = transaction_list.order_by('-date')

    paginator = Paginator(transaction_list, 15) # Show 25 contacts per page
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    input_source_list = InputSource.objects.filter(owner=request.user)
    context = {'transactions':  transactions,
               'startDate': start_date, 'endDate': end_date,
               'inputSources': input_source_list,
               'source': source,
               'search': search,
               'categories': Category.objects.filter(owner=request.user).order_by('text'),
               'category': category_id,
               'subcategory': subcategory_id,
               'subcategories': SubCategory.objects.filter(owner=request.user).order_by('text'),
               }

    return render(request, 'expenses/index.html', context)


def detail(request, txn_id):
    transaction = get_object_or_404(Transaction, pk=txn_id)
    return render(request, 'expenses/detail.html', {'transaction': transaction,
                                                    'subCatagories':SubCategory.objects.all()})


def index_action(request):
    marked_transactions = request.POST.getlist('marked_checkbox')
    start_date = request.POST['startDate']
    end_date = request.POST['endDate']
    source = request.POST['source']
    search = request.POST['search']
    category = request.POST['category']
    current_subcategory = request.POST['subcategory']
    page = request.POST['page']

    if request.POST['action'] == 'delete':
        for marked in marked_transactions:
            transaction = Transaction.objects.get(owner=request.user, pk=int(marked))
            transaction.delete()

    if request.POST['action'] == 'bulk_update':
        subcategory_id = request.POST['bulk_subcategory']
        new_subcategory = SubCategory.objects.get(owner=request.user, pk=int(subcategory_id))
        for marked in marked_transactions:
            transaction = Transaction.objects.get(owner=request.user, pk=int(marked))
            transaction.subcategory = new_subcategory
            transaction.save()

    url = reverse('expenses:index') + "?startDate=" + start_date + "&endDate=" + end_date + '&source=' + source \
          + '&search' + search + '&category=' + category + '&subcategory=' + str(current_subcategory) + '&page='+page
    return HttpResponseRedirect(url)


def save_post(request):
    transaction_id = request.POST['transaction_id']
    subcategory_id = request.POST['subcategory_id']

    transaction = Transaction.objects.get(owner=request.user, pk=transaction_id)
    new_subcategory = SubCategory.objects.get(owner=request.user, pk=subcategory_id)

    transaction.subcategory = new_subcategory
    transaction.save()

    data = {}
    return JsonResponse(data)

