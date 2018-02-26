from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from expenses.common import ANYTEXT_CONTAINS_RULE_TEXT
from expenses.models import SubCategory, RuleType, Rule, Transaction


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
        subcategory = None
        if move_to != 'delete':
            subcategory = SubCategory.objects.get(owner=request.user, pk=move_to)
        # rule_type = RuleType.objects.get(pk=request.POST['rule_type_id'])
    except (KeyError, SubCategory.DoesNotExist) as e:
        return render(request, 'expenses/categories', {'error_message': "All fields mandatory",})
    else:

        new_rule = Rule(owner=request.user, rule_type=None, subCategory=subcategory, value=value)
        new_rule.save()
        apply_rule(new_rule, request.user)
        return HttpResponseRedirect(reverse('expenses:rules'))


def apply_rule(rule, user):
    # if rule.rule_type.text == ANYTEXT_CONTAINS_RULE_TEXT:
    transactions = Transaction.objects.filter(owner=user)\
        .filter(Q(merchant__icontains=rule.value) | Q(comment__icontains=rule.value))
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