from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from expenses.models import SubCategory, RuleType, Rule, Transaction


def rules(request):
    rules = Rule.objects.all()
    rule_types = RuleType.objects.all()
    subcategories = SubCategory.objects.all()
    context = {'rules': rules,
               'rule_types': rule_types,
               'subcategories': subcategories}
    return render(request, 'expenses/rules.html', context)


def rules_add(request):
    try:
        value = request.POST['value']
        subcategory = SubCategory.objects.get(pk=request.POST['subcategory_id'])
        rule_type = RuleType.objects.get(pk=request.POST['rule_type_id'])
    except (KeyError, RuleType.DoesNotExist, SubCategory.DoesNotExist) as e:
        return render(request, 'expenses/categories', {'error_message': "All fields mandatory",})
    else:
        new_rule = Rule(rule_type=rule_type,subCategory=subcategory,value=value)
        new_rule.save()
        return HttpResponseRedirect(reverse('expenses:rules'))


def apply_rule(rule):
    if rule.rule_type.text == 'AnyText_Contains':
        transactions = Transaction.objects.filter(Q(merchant__icontains=rule.value) | Q(comment__icontains=rule.value))
        for transaction in transactions:
            transaction.subcategory = rule.subCategory
            transaction.save()


def rules_action(request):
    marked_rules = request.POST.getlist('marked_checkbox')
    if request.POST['action'] == 'delete':
        for marked in marked_rules:
            rule = Rule.objects.get(pk=marked)
            rule.delete()
    elif request.POST['action'] == 'apply':
        for marked in marked_rules:
            rule = Rule.objects.get(pk=marked)
            apply_rule(rule)
    return HttpResponseRedirect(reverse('expenses:rules'))