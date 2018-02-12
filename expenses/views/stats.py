from datetime import datetime, timedelta
from itertools import groupby

import dateutil
import pygal
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse
from pygal.style import Style

from expenses.models import Transaction, Category
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from django.shortcuts import render, render_to_response


def stats_month_category(request, month, category_str):
    Config = pygal.Config()
    Config.tooltip_fancy_mode = False
    date = datetime.strptime(month, '%b %Y')
    start_date = date.replace(day=1)
    end_date = start_date + dateutil.relativedelta.relativedelta(months=1) + timedelta(-1)

    category = Category.objects.get(owner=request.user, text=category_str)

    transactions = Transaction.objects.filter(owner=request.user, subcategory__category=category)\
        .filter(date__range=[start_date, end_date])\
        .order_by('-subcategory')

    total_sum = 0

    pie_chart = pygal.Pie(Config)

    for key, subcategory in groupby(transactions, lambda x: x.subcategory):

        subcategory_sum = 0
        for transaction in subcategory:
            subcategory_sum = subcategory_sum + transaction.amount
            subcategory_object = transaction.subcategory

        url = request.build_absolute_uri(reverse('expenses:index') + "?startDate=" + start_date.strftime('%Y-%m-%d')
                                         + "&endDate=" + end_date.strftime('%Y-%m-%d')
                                         + '&subcategory=' + str(subcategory_object.id))

        total_sum = total_sum + subcategory_sum
        pie_chart.add(subcategory_object.text, [{'value':subcategory_sum,
                                                'xlink': {'href': url, 'target': '_top'}}])


    pie_chart.title = month + " " + category_str + '\nTotal ' + str('{:20,d}'.format(int(total_sum))) + "₪"

    pie_chart.render()
    pie_chart = pie_chart.render_data_uri()
    context = {'chart': pie_chart}

    return render(request, 'expenses/stats.html', context)


def stats_month(request, month):
    Config = pygal.Config()
    Config.tooltip_fancy_mode = False
    date = datetime.strptime(month, '%b %Y')
    start_date = date.replace(day=1)
    end_date = start_date + dateutil.relativedelta.relativedelta(months=1) + timedelta(-1)

    transaction = Transaction.objects.filter(owner=request.user).filter(date__range=[start_date, end_date]).order_by('-subcategory')

    pie_map = {}
    total_sum = 0
    for key, subcategory in groupby(transaction, lambda x: x.subcategory):
        subcategory_sum = 0
        subcategory_object = None
        for transaction in subcategory:
            subcategory_sum = subcategory_sum + transaction.amount
            subcategory_object = transaction.subcategory

        total_sum = total_sum + subcategory_sum
        if subcategory_object is None:
            category_id=-1
            category_str = 'UnTagged'
        else:
            category_id = subcategory_object.category.id
            category_str = str(subcategory_object.category)

        if subcategory_object is None:
            subcategory_label = 'UnTagged'
        else:
            subcategory_label = str(subcategory_object)

        url = request.build_absolute_uri(reverse('expenses:index') + "?startDate=" + start_date.strftime('%Y-%m-%d')
                                         + "&endDate=" + end_date.strftime('%Y-%m-%d') + '&category='
                                         + str(category_id))

        subcategory_pie_map = {'value': int(subcategory_sum),'label': subcategory_label,'xlink':{'href': url, 'target': '_top'}}
        if category_str in pie_map:
            pie_map[category_str].append(subcategory_pie_map)
        else:
            pie_map[category_str] = [subcategory_pie_map]

    custom_style = Style(
        # background='transparent',
        # plot_background='transparent',
        # opacity='.6',
        # opacity_hover='.9',
        # transition='400ms ease-in',
        tooltip_font_size=10
        )

    pie_chart = pygal.Pie(Config)
    pie_chart.title = month + '\nTotal ' + str('{:20,d}'.format(int(total_sum))) + "₪"
    for category in pie_map:
        # pie_chart.add(category, pie_map[category])
        url = request.build_absolute_uri(reverse('expenses:stats_month_category', kwargs={'month': month,'category_str': category}))

        pie_chart.add(category, [{'value':sum(x['value'] for x in pie_map[category]),
                                  'xlink':{'href': url, 'target': '_top'}}])


    pie_chart.render()
    pie_chart = pie_chart.render_data_uri()
    context = {'chart': pie_chart}

    return render(request, 'expenses/stats_month.html', context)


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
    context = {'chart': chart}

    return render(request, 'expenses/stats.html', context)

