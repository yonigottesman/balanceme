from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from expenses.common import UNTAGGED_SUBCATEGORY_TEXT
from expenses.models import SubCategory, Category, Rule, RuleType


def categories(request):
    sub_categories = SubCategory.objects.filter(owner=request.user).order_by('category')
    all_categories = Category.objects.filter(owner=request.user).order_by('text')
    context = {
        'sub_categories': sub_categories,
        'categories': all_categories
    }

    return render(request, 'expenses/categories.html', context)


def categories_add(request):
    try:
        text = request.POST['text']
    except KeyError:
        # Redisplay the transaction voting form.
        return render(request, 'expenses/categories', { 'error_message': "All fields mandatory",})
    else:
        if text != '' and text != UNTAGGED_SUBCATEGORY_TEXT:
            category = Category(text=text, owner=request.user)
            category.save()
        return HttpResponseRedirect(reverse('expenses:categories'))


def sub_categories_add(request):
    try:
        text = request.POST['text']
        category_id = request.POST['category_id']
        category = Category.objects.get(pk=category_id, owner=request.user)
    except (KeyError, Category.DoesNotExist):
        # Redisplay the transaction voting form.
        return render(request, 'expenses/categories', {'error_message': "All fields mandatory"})
    else:
        if text != '' and text != UNTAGGED_SUBCATEGORY_TEXT:
            sub_category = SubCategory(text=text, category=category, owner=request.user)
            sub_category.save()
        return HttpResponseRedirect(reverse('expenses:categories'))


def categories_action(request):
    marked_categories = request.POST.getlist('marked_checkbox')
    if request.POST['action'] == 'delete':
        for marked in marked_categories:
            category = Category.objects.get(pk=marked, owner=request.user)
            if category.text != UNTAGGED_SUBCATEGORY_TEXT:
                subcategories = [x.id for x in category.subcategory_set.filter(owner=request.user)]
                delete_subcategories(request.user, subcategories)
                category.delete()
    return HttpResponseRedirect(reverse('expenses:categories'))


def delete_subcategories(user, subcategory_ids):
    for marked in subcategory_ids:
        sub_category = SubCategory.objects.get(pk=marked, owner=user)
        if sub_category.text != UNTAGGED_SUBCATEGORY_TEXT:
            transactions = sub_category.transaction_set.filter(owner=user)
            notagging_subcategory = SubCategory.objects.get(owner=user, text=UNTAGGED_SUBCATEGORY_TEXT)
            transactions.update(subcategory=notagging_subcategory)
            sub_category.delete()


def sub_categories_action(request):
    marked_sub_categories = request.POST.getlist('marked_checkbox_sub')
    if request.POST['action'] == 'delete':
        delete_subcategories(request.user, marked_sub_categories)
    return HttpResponseRedirect(reverse('expenses:categories'))
