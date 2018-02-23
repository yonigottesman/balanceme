from datetime import datetime, timedelta
from itertools import groupby

import dateutil
import pygal
from django.db.models import Q
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse
from pygal.style import Style

from expenses.common import UNTAGGED_SUBCATEGORY_TEXT, get_untagged_category, get_datetime
from expenses.models import Transaction, Category, InputSource
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from django.shortcuts import render, render_to_response


def stats_manual(request):
    try:
        start_date = get_datetime(request.POST['startDate'])
        end_date = get_datetime(request.POST['endDate'])
        source = request.POST['source']
        search = request.POST['search']

    except KeyError:
        # Redisplay the transaction voting form.
        return render(request, 'expenses/stats.html', {})
    else:
        pie_chart = category_piechart(request=request, start_date=start_date, end_date=end_date,
                                      search_text=search, input_source=source)

        context = {'chart': pie_chart}
        return render(request, 'expenses/stats.html', context)
        pass


def stats_category(request, category):

    start_date = get_datetime(request.GET.get('startDate'))
    end_date = get_datetime(request.GET.get('endDate'))
    input_source = request.GET.get('source')
    search_text= request.GET.get('search')


    Config = pygal.Config()
    Config.tooltip_fancy_mode = False

    category = Category.objects.get(owner=request.user, pk=category)

    transactions = Transaction.objects.filter(owner=request.user, subcategory__category=category).order_by('-subcategory')
    url_params = '?category=' + str(category.id)

    if search_text is not None:
        transactions = transactions.filter(Q(merchant__icontains=search_text) | Q(comment__icontains=search_text))
        url_params = url_params + '&search=' + search_text
    if start_date is not None:
        transactions = transactions.filter(date__gte=start_date)
        url_params = url_params + "&startDate=" + start_date.strftime('%Y-%m-%d')
    if end_date is not None:
        transactions = transactions.filter(date__lte=end_date)
        url_params = url_params + "&endDate=" + end_date.strftime('%Y-%m-%d')
    if input_source is not None and input_source != 'all':
        url_params = url_params + "&source=" + input_source
        transactions = transactions.filter(source_id=int(input_source))


    total_sum = 0
    pie_chart = pygal.Pie(Config)

    for subcategory, subcategory_list in groupby(transactions, lambda x: x.subcategory):

        subcategory_sum = sum([tx.amount for tx in subcategory_list])
        total_sum = total_sum + subcategory_sum

        url = request.build_absolute_uri(reverse('expenses:index') + url_params + '&subcategory=' + str(subcategory.id))

        pie_chart.add(subcategory.text, [{'value':subcategory_sum,
                                                'xlink': {'href': url, 'target': '_top'}}])

    pie_chart.title = subcategory.text + '\nTotal ' + str('{:20,d}'.format(int(total_sum))) + "₪"

    pie_chart.render()
    pie_chart = pie_chart.render_data_uri()
    context = {'chart': pie_chart}

    return render(request, 'expenses/stats.html', context)


def category_piechart(request, start_date, end_date, search_text, input_source):

    transactions = Transaction.objects.filter(owner=request.user).order_by('-subcategory')
    url_params = '?category=' + str(get_untagged_category(request.user).id)

    if search_text is not None:
        transactions = transactions.filter(Q(merchant__icontains=search_text) | Q(comment__icontains=search_text))
        url_params=url_params+'&search='+search_text
    if start_date is not None:
        transactions = transactions.filter(date__gte=start_date)
        url_params = url_params + "&startDate=" + start_date.strftime('%Y-%m-%d')
    if end_date is not None:
        transactions = transactions.filter(date__lte=end_date)
        url_params = url_params + "&endDate=" + end_date.strftime('%Y-%m-%d')
    if input_source is not None and input_source != 'all':
        url_params = url_params + "&source=" + input_source
        transactions = transactions.filter(source_id=int(input_source))

    config = pygal.Config()
    config.tooltip_fancy_mode = False

    pie_chart = pygal.Pie(config)

    total_sum = 0
    for category, category_list in groupby(transactions, lambda x: x.subcategory.category):


        category_sum = sum([txn.amount for txn in category_list])
        total_sum = total_sum + category_sum

        if category.text == UNTAGGED_SUBCATEGORY_TEXT:
            url = request.build_absolute_uri(reverse('expenses:index') + url_params)
        else:
            url = request.build_absolute_uri(reverse('expenses:stats_category', kwargs={'category': (category.id)}) + url_params)

        pie_chart.add(category.text, [{'value':category_sum,
                                  'xlink': {'href': url, 'target': '_top'}}])

    pie_chart.title = start_date.strftime('%Y-%m-%d') + "   <->   " + end_date.strftime('%Y-%m-%d')\
                      + '\nTotal ' + str('{:20,d}'.format(int(total_sum))) + "₪"

    pie_chart.render()
    pie_chart = pie_chart.render_data_uri()
    return pie_chart


def stats_month(request, month):

    date = datetime.strptime(month, '%b %Y')
    start_date = date.replace(day=1)
    end_date = start_date + dateutil.relativedelta.relativedelta(months=1) + timedelta(-1)

    pie_chart = category_piechart(request=request,start_date=start_date, end_date=end_date,
                                  search_text=None, input_source=None)

    context = {'chart': pie_chart}

    return render(request, 'expenses/stats.html', context)


def stats(request):
    Config = pygal.Config()
    Config.tooltip_fancy_mode=False
    # Config.tooltip_border_radius=100
    #Config.js = []
    date_list = [datetime.today() - dateutil.relativedelta.relativedelta(months=x) for x in range(11, -1, -1)]

    sum_list = []
    for date in date_list:
        sum_list.append(Transaction.objects.filter(owner=request.user).filter(date__year=date.year, date__month=date.month).aggregate(Sum('amount'))['amount__sum'])

    str_month_list = [datetime.strftime(x, '%b %Y') for x in date_list]

    chart = pygal.Bar(Config)
    chart.x_labels = str_month_list
    bar_list = []
    chart.force_uri_protocol = 'http'
    for i in range(len(sum_list)):
        url = request.build_absolute_uri(reverse('expenses:stats_month', kwargs={'month': str_month_list[i]}))
        dict = {
            'value': sum_list[i],
            'label': str_month_list[i],
            'xlink': {'href': url, 'target': '_top'},

        }
        bar_list.append(dict)

    chart.add(None, bar_list)

    chart = chart.render_data_uri(force_uri_protocol='https')
    input_sources = InputSource.objects.filter(owner=request.user)
    context = {'chart': chart,
               'inputSources': input_sources}

    return render(request, 'expenses/stats.html', context)

