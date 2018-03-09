from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from expenses.common import get_untagged_subcategory
from expenses.models import SubCategory, RuleType, Rule, Transaction, InputSource


def rules(request):
    rules = Rule.objects.filter(owner=request.user).order_by('subCategory')
    rule_types = RuleType.objects.all()
    subcategories = SubCategory.objects.filter(owner=request.user).order_by('text')
    context = {'rules': rules,
               'rule_types': rule_types,
               'subcategories': subcategories}
    return render(request, 'expenses/rules.html', context)


def rules_add(request):
    try:
        value = request.POST['value']
        move_to = request.POST['subcategory_id']
        source = request.POST['source_id']
        amount = request.POST['amount']
        day = request.POST['day']
        subcategory = None
        if move_to != 'delete':
            subcategory = SubCategory.objects.get(owner=request.user, pk=move_to)
        if amount == '':
            amount = None
        else:
            amount = float(amount)

        if source == 'Any':
            source = None
        else:
            source = InputSource.objects.get(pk=source, owner=request.user)

        if day == '0':
            day = None
        else:
            day = int(day)

        if value == '':
            value = None

        # rule_type = RuleType.objects.get(pk=request.POST['rule_type_id'])
    except (KeyError, SubCategory.DoesNotExist) as e:
        return render(request, 'expenses/categories', {'error_message': "All fields mandatory",})
    else:

        new_rule = Rule(owner=request.user, rule_type=None, subCategory=subcategory, value=value,
                        source=source, amount=amount, day=day)
        new_rule.save()
        apply_rule(new_rule, request.user)
        return HttpResponseRedirect(reverse('expenses:rules'))


def apply_rule(rule, user):

    transactions = Transaction.objects.filter(owner=user)

    if rule.value is not None:
        transactions = transactions.filter(Q(merchant__icontains=rule.value) | Q(comment__icontains=rule.value))

    if rule.source is not None:
        transactions = transactions.filter(source=rule.source)

    if rule.amount is not None:
        transactions = transactions.filter(amount=rule.amount)

    if rule.day is not None:
        transactions = transactions.filter(date__day=rule.day)


    for transaction in transactions:
        if rule.subCategory is None:
            transaction.delete()
        else:
            transaction.subcategory = rule.subCategory
            transaction.save()


def rules_action(request):
    marked_rules = request.POST.getlist('marked_checkbox')
    if request.POST['action'] == 'delete':
        for marked in marked_rules:
            rule = Rule.objects.get(owner=request.user, pk=marked)
            rule.delete()
    elif request.POST['action'] == 'apply':
        for marked in marked_rules:
            rule = Rule.objects.get(owner=request.user, pk=marked)
            apply_rule(rule, request.user)
    return HttpResponseRedirect(reverse('expenses:rules'))