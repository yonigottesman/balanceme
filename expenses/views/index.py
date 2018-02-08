from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import dateutil.parser

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
    category_id = request.GET.get('category')

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
        transaction_list = transaction_list.filter(owner=request.user, subcategory__category=category)
        category_id = int(category_id)

    transaction_list = transaction_list.order_by('-date')

    paginator = Paginator(transaction_list, 15) # Show 25 contacts per page
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    input_source_list = InputSource.objects.all()
    context = {'transactions':  transactions,
               'startDate': start_date, 'endDate': end_date,
               'inputSources': input_source_list,
               'source': source,
               'search': search,
               'categories': Category.objects.filter(owner=request.user),
               'category': category_id,
               'subcategories': SubCategory.objects.filter(owner=request.user),
               }

    return render(request, 'expenses/index.html', context)


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


def index_action(request):
    marked_transactions = request.POST.getlist('marked_checkbox')
    start_date = request.POST['startDate']
    end_date = request.POST['endDate']
    source = request.POST['source']
    search = request.POST['search']
    category = request.POST['category']

    if request.POST['action'] == 'delete':
        for marked in marked_transactions:
            transaction = Transaction.objects.get(owner=request.user, pk=int(marked))
            transaction.delete()
    url = reverse('expenses:index') + "?startDate=" + start_date + "&endDate=" + end_date + '&source=' + source \
          + '&search' + search + '&category='+ category
    return HttpResponseRedirect(url)


def save_post(request):
    transaction_id = request.POST['transaction_id']
    subcategory_id = request.POST['subcategory_id']

    transaction = Transaction.objects.get(owner=request.user, pk=transaction_id)
    new_subcategory = SubCategory.objects.get(owner=request.user, pk= subcategory_id)

    transaction.subcategory = new_subcategory
    transaction.save()

    data = {}
    return JsonResponse(data)

